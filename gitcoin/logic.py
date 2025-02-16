from dataclasses import dataclass, field
from git import Repo, Commit
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
import re

from gitcoin.utils import simple_to_pem

def make_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024
    )

    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize the public key to PEM format (bytes) and then decode to a string
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return [private_pem.decode(), public_pem.decode()]


def _construct_message(pubkey, srcs, dests, fee):
    srcs_str = '\n'.join(map(lambda a: a.strip(), srcs))
    dests_str = '\n'.join(map(lambda a: f"{a[1]} {a[0]}", dests.items()))
    return f"{pubkey}\n\n{srcs_str}\n{dests_str}\n{fee}".encode()

@dataclass
class TnxInfo:
    # pubkey is the public key of the user sending the money
    pubkey: str

    # srcs is a list of sources for transactions
    srcs: list[str]

    # map from destination public key to amount to send
    dests: dict[str, int]

    # fee allocated to the miner
    mining_fee: int

    # signature
    signature: str

    @staticmethod
    def from_str(s: str):
        tnx_match = re.match(r"(\S+)\n\n((?:\S+\n)*)((?:\d+ \S+\n)*(?:\d+ \S+))\n(\d)\n(\S+)", s)
        if tnx_match is None or len(tnx_match.groups()) != 5:
            return None

        [pubkey, srcs_raw, dests_raw, fee, signature] = tnx_match.groups()
        srcs = srcs_raw.strip().split("\n")
        dests = {pubkey: int(amount) for [amount, pubkey] in map(lambda a: a.split(" "), dests_raw.split("\n"))}
    
        return TnxInfo(pubkey, srcs, dests, int(fee), signature)

    @staticmethod
    def sign(privkey, pubkey, srcs, dests, fee):
        """Sign the transaction using the private key."""
        
        # Create a string to sign that includes relevant transaction details
        signature = load_pem_private_key(simple_to_pem(privkey, True).encode(), None).sign(
            _construct_message(pubkey, srcs, dests, fee),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return TnxInfo(pubkey, srcs, dests, fee, signature.hex())


    def validate(self):
        try:
            load_pem_public_key(simple_to_pem(self.pubkey, False).encode()).verify(
                bytes.fromhex(self.signature),
                _construct_message(self.pubkey, self.srcs, self.dests, self.mining_fee),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

        except Exception as e:
            return False

        return True
        

    def __str__(self):
        srcs_str = '\n'.join(map(lambda a: a.strip(), self.srcs))
        dests_str = '\n'.join(map(lambda a: f"{a[1]} {a[0]}", self.dests.items()))
        return f"{self.pubkey}\n\n{srcs_str}\n{dests_str}\n{self.mining_fee}\n{self.signature}"


@dataclass
class Tnx(TnxInfo):
    # hash is the commit hash
    hash: str

    # prev_hash is the hash of the previous commit
    prev_hash: str

    @staticmethod
    def from_info(hash: str, prev_hash: str, info: TnxInfo):
        return Tnx(info.pubkey, info.srcs, info.dests, info.mining_fee, info.signature, hash, prev_hash)


@dataclass
class Block:
    hash: str
    owner: str
    worth: int = 0
    tnxs: list[Tnx] = field(default_factory=list)

    @staticmethod
    def from_commit(commit):
        match = re.match(r"(\d+) (.+)\n\n.+", commit.message)
        if match is None:
            return None

        [worth, owner] = match.groups()
        return Block(commit.hexsha, owner, int(worth))

    def __str__(self):
        return f"{self.worth} {self.owner}\n\n{self.hash}"
    

@dataclass
class State:
    tnxs: dict[str, Tnx] = field(default_factory=dict)
    mempool: list[TnxInfo] = field(default_factory=list)
    blocks: dict[str, Block] = field(default_factory=dict)
    repo: Repo = None
    repo_location: str = ""
    pubkey: str = ""
    privkey: str = ""

    
@dataclass
class RemoteState:
    tnxs: dict[str, Tnx] = field(default_factory=dict)
    mempool: list[TnxInfo] = field(default_factory=list)
    blocks: dict[str, Block] = field(default_factory=dict)


def validate_tnx(to_validate: TnxInfo, s: State):
    #tnx should exist
    if not to_validate:
        return False

    #source should exist
    for src in to_validate.srcs:
        if src not in s.tnxs:
            return False

    #amnts should be the same
    amnt_to_spend = to_validate.mining_fee 
    for dest in to_validate.dests:
        if to_validate.dests[dest] < 0:
            return False

        amnt_to_spend += to_validate.dests[dest]

    
    for src in to_validate.srcs:
        src_tnx = s.tnxs[src]
        if to_validate.pubkey not in src_tnx.dests:
            return False 
        amnt_to_spend -= src_tnx.dests[to_validate.pubkey]

    if amnt_to_spend != 0:
        return False


    #no other tnx should point to the same
    for hash in s.tnxs:
        if s.tnxs[hash].pubkey != to_validate.pubkey:
            continue

        for src in s.tnxs[hash].srcs:
            if src in to_validate.srcs:
                return False


    #tnx is good
    return True


#validates block and updates tnx_map
def validate_tnxi(s: State, tnxi: TnxInfo):
    if not tnxi.validate():
        return False

    if not validate_tnx(tnxi, s):
        return False

    # no double counting sources
    for tnx in s.mempool:
        for src in tnx.srcs:
            if src in tnxi.srcs:
                return False

    return True



def init_chain(state: State):
    """constructs the commit hash -> Tnx map from the repo"""

    if not state.repo.heads:
        return


    state.tnxs = {}
    state.mempool = []
    state.blocks = {}

    last_block = None
    for commit in state.repo.iter_commits():
        if last_block is None:

            if (bloc := Block.from_commit(commit)) is not None:
                last_block = bloc

            elif (tnx := TnxInfo.from_str(commit.message)) is not None:
                state.mempool.append(tnx)

            continue

        assert len(commit.parents) <= 1 # you can have multiple parents in a merge, we should never have a merge
    
        
        # if we're a block, ignore
        if (bloc := Block.from_commit(commit)) is not None:
            state.blocks[commit.hexsha] = last_block
            last_block = bloc
            continue

        tnx_info = TnxInfo.from_str(commit.message)
        if len(commit.parents):
            tnx = Tnx.from_info(commit.hexsha, commit.parents[0].hexsha, tnx_info)
        else:
            tnx = Tnx.from_info(commit.hexsha, None, tnx_info)
            
        state.tnxs[tnx.hash] = tnx
        last_block.tnxs.append(tnx)

    if last_block is not None:
        state.blocks[last_block.hash] = last_block


def match_block(s: str) -> re.Match:
    return re.match(r"(.+)\n\n(.+)", s)

def match_transaction(s: str) -> re.Match:
    return re.match(r"(.+)\n\n((?:.+\n)+)((?:(?:\d+ .+\n)*(?:\d+ .+))\n|())(\d)\n(.+)", s)


def append_block(s: State, header: str):
    """appends a block with a given header"""
    block = Block.from_commit(next(s.repo.iter_commits()))

    # TODO: validate the amount of zeros
    # TODO: make the amount of zeros required depend on how long it took to make the last block
    # TODO: move each commit we have from mempool to tnxs


def rebase_on_remotes(s: State):
    """
    updates the chain based on the remotes
    adds all valid pending transactions the other chains have

    if a longer, valid chain is found, reset to that chain and add
    all pending transactions not on that chain after
    """
    for remote in s.repo.remotes:
        if remote.name == "origin": continue
        
        remote.fetch()
        
        rs = RemoteState()
        last_block = None
        recent_common_commit = None
        for commit in s.repo.iter_commits(f"{remote.name}/main"):

            if commit.hexsha in s.blocks or commit.hexsha in s.tnxs:
                recent_common_commit = commit
                break
            
            if last_block is None:
                if (bloc := Block.from_commit(commit)) is not None:
                    last_block = bloc
                else:
                    rs.mempool.append(TnxInfo.from_str(commit.message))
                continue

            if (bloc := Block.from_commit(commit)) is not None:
                rs.blocks[commit.hexsha] = last_block
                last_block = bloc
                continue
            
            tnx_info = TnxInfo.from_str(commit.message)
            if len(commit.parents):
                tnx = Tnx.from_info(commit.hexsha, commit.parents[0].hexsha, tnx_info)
            else:
                tnx = Tnx.from_info(commit.hexsha, None, tnx_info)
            rs.tnxs[commit.hexsha] = tnx
            last_block.tnxs.append(tnx)

        if last_block is not None:
            rs.blocks[last_block.hash] = last_block



        tnx_hashes = []
        block_hashes = []
        for commit in s.repo.iter_commits():
            if commit.hexsha == recent_common_commit.hexsha:
                break
            
            if (bloc := Block.from_commit(commit)) is not None:
                block_hashes.append(bloc.hash)
            else:
                tnx_hashes.append(commit.hexsha)

        # if we have more blocks, we have to reset on that chain
        if len(rs.blocks) > len(block_hashes):
            remote_latest_commit = next(s.repo.iter_commits(f"{remote.name}/main"))
            s.repo.git.reset("--hard", remote_latest_commit.hexsha)

            # remove everything in rs2 form s
            try:
                for hash in block_hashes: 
                    del s.blocks[hash]
            except:
                pass

            # add everything in rs to s
            for hash, tnx in rs.tnxs.items():
                s.tnxs[hash] = tnx
            for hash, block in rs.blocks.items():
                s.blocks[hash] = tnx

            # try to add anything else we can add
            for hash in tnx_hashes:
                if validate_tnxi(s, tnx):
                    commit_transaction(s, tnx)
                else:
                    del s.tnxs[hash]

        # otherwise put everything we can into mempool
        else:
            for tnx in [*rs.tnxs.values()] + rs.mempool:
                if validate_tnxi(s, tnx):
                    commit_transaction(s, tnx)
        

def commit_transaction(s: State, tnx_i: TnxInfo):
    s.repo.git.commit("--allow-empty", "-m", f"{str(tnx_i)}")
    s.mempool.append(tnx_i)

