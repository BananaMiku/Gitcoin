from dataclasses import dataclass, field
from git import Repo, Commit
import re
from ecdsa import VerifyingKey, SECP256k1
from ecdsa.util import string_to_number

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
        tnx_match = match_transaction(s)
        assert tnx_match is not None
        assert len(tnx_match.groups()) == 5

        [pubkey, srcs_raw, dests_raw, fee, signature] = tnx_match.groups()
        srcs = srcs_raw.split("\n")
        dests = {pubkey: int(amount) for [amount, pubkey] in map(lambda a: a.split(" "), dests_raw.split("\n"))}
    
        return TnxInfo(pubkey, srcs, dests, int(fee), signature)

    @staticmethod
    def sign(self, privkey, pubkey, srcs, dests, fee):
        """Sign the transaction using the private key."""
        
        # Create a string to sign that includes relevant transaction details
        data_to_sign = f"{pubkey}{srcs}{dests}{fee}".encode()

        signature = self._generate_signature(data_to_sign, privkey)

        return TnxInfo(pubkey, srcs, dests, fee, signature)

    def validate(self, strToBeValidated: str):
        # validate signature
        # Create a VerifyingKey object from the public key
        pubkey_bytes = bytes.fromhex(self.pubkey)  # Convert the hex public key to bytes
        verifying_key = VerifyingKey.from_string(pubkey_bytes, curve=SECP256k1)

        try: 
            is_valid = verifying_key.verify(bytes.fromhex(self.signature), strToBeValidated)
            return is_valid  # Return True if the signature is valid
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False  # Return False if verification fails or an error occurs

    def _generate_signature(self, data: bytes, privkey: str) -> bytes:
        """
        Generate a Schnorr signature for the given data using the provided private key.
        
        :param data: The data to sign as bytes.
        :param privkey: The private key as a hexadecimal string.
        :return: The Schnorr signature as bytes.
        """
        # Create a SigningKey object using the provided private key
        privkey_bytes = bytes.fromhex(privkey)  # Convert the hex private key to bytes
        signing_key = SigningKey.from_string(privkey_bytes, curve=SECP256k1)

        # Generate the Schnorr signature
        signature = signing_key.sign(data)

        return signature  # Return the signature as bytes

    def __str__(self):
        srcs_str = '\n'.join(self.srcs)
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
        match = re.match(r"(\d+) (\w+)\n\n\w+", commit.message)
        if match is None:
            return None

        [worth, owner] = match.groups()
        return Block(commit.hash, owner, worth)


@dataclass
class State:
    tnxs: dict[str, Tnx]
    mempool: list[TnxInfo]
    blocks: dict[str, Block]
    repo: Repo
    pubkey: str
    privkey: str

    
@dataclass
class RemoteState:
    tnxs: dict[str, Tnx]
    mempool: list[TnxInfo]
    blocks: dict[str, Block]


def validate_tnx(to_validate: Tnx, s: State):
    #tnx should exist
    if not to_validate:
        print("need valid tnx obj")
        return False

    #source should exist
    for src in to_validate.srcs:
        if src not in s.tnxs:
            print(f"source: {src} does no exist")
            return False

    #amnts should be the same
    amnt_to_spend = to_validate.mining_fee 
    for dest in to_validate.dests:
        if to_validate.dests[dest] < 0:
            print("cant have neg amounts") 
            return False

        amnt_to_spend += to_validate.dests[dest]
    print(f"{amnt_to_spend}")

    
    for src in to_validate.srcs:
        src_tnx = s.tnxs[src]
        if to_validate.pubkey not in src_tnx.dests:
            return False 
        amnt_to_spend -= src_tnx.dests[to_validate.pubkey]

    if amnt_to_spend != 0:
        print("incorrect amnts")
        return False


    #no other tnx should point to the same
    for hash in s.tnxs:
        if s.tnxs[hash].pubkey != to_validate.pubkey:
            continue

        for src in s.tnx[hash].srcs:
            if src in to_validate.srcs:
                print("cant source same tnx twice")
                return False


    #tnx is good
    return True


#validates block and updates tnx_map
def validate_block(added_tnxs: [Tnx], s: State):
    for i, tnx in enumerate(added_tnx):
        if not validate_tnx(tnx, s):
            #clears everything we added
            for j in range(i):
                del s.tnxs[added_tnx[j].hash]

            return False
        s.tnxs[tnx.hash] = tnx

    return True


def init_chain(state: State):
    """constructs the commit hash -> Tnx map from the repo"""

    state.tnxs = {}
    state.mempool = []
    state.blocks = {}

    last_block = None
    for commit in state.repo.iter_commits():

        if last_block is None:

            if match_block(commit.message) is not None:
                last_block = Block.from_commit(commit)

            else:
                state.mempool.append(TnxInfo.from_str(commit.message))

            continue

        assert len(commit.parents) == 1 # you can have multiple parents in a merge, we should never have a merge
    
        # if we're a block, ignore
        if match_block(commit.message) is not None:
            last_block.worth = sum(map(lambda a: a.mining_fee, last_block.tnxs))
            state.blocks[commit.hash] = last_block
            last_block = Block.from_commit(commit)

        tnx_info = TnxInfo.from_str(commit.message)
        tnx = Tnx.from_info(commit.hash, commit.parents[0], tnx_info)
        state.tnxs[tnx.hash] = tnx
        last_block.tnxs.append(tnx)

    last_block.worth = sum(map(lambda a: a.mining_fee, last_block.tnxs))
    state.blocks[last_block.hash] = last_block


def match_block(s: str) -> re.Match:
    return re.match(r"(\w+)\n\n(\w+)", s)

def match_transaction(s: str) -> re.Match:
    return re.match(r"(\w+)\n\n((?:\w+\n)+)((?:\d+ \w+\n)+)(\d)\n(\w+)", s)


def append_block(s: State, header: str):
    """appends a block with a given header"""
    s.repo.git.commit("--empty-commit", "-m", f"\"{header}\n\n{s.pubkey}\"")
    # TODO: validate the amount of zeros
    # TODO: make the amount of zeros required depend on how long it took to make the last block


def rebase_on_remotes(s: State) -> list[str]:
    """
    updates the chain based on the remotes
    adds all valid pending transactions the other chains have

    if a longer, valid chain is found, reset to that chain and add
    all pending transactions not on that chain after
    """
    for remote in s.repo.remotes:
        remote.fetch()
        blocks = 0
        
        rs = RemoteState()
        last_block = None
        recent_common_commit = None
        for commit in s.repo.iter_commits(f"{remote.name}/main"):

            if commit.hash in blocks_set or commit.hash in s.tnxs:
                recent_common_commit = commit
            
            if last_block is None:
                if match_block(commit.message) is not None:
                    last_block = Block.from_commit(commit)
                else:
                    rs.mempool.append(TnxInfo.from_str(commit.message))
                continue

            if match_block(commit.message) is not None:
                last_block.worth = sum(map(lambda a: a.mining_fee, last_block.tnxs))
                rs.blocks[commit.hash] = last_block
                last_block = Block.from_commit(commit)
            
            tnx_info = TnxInfo.from_str(commit.message)
            tnx = Tnx(commit.hash, commit.parents[0].hash, tnx_info)
            rs.tnxs[commit.hash] = tnx
            rs.last_block.tnxs.append(tnx)

        if last_block is not None:
            last_block.worth = sum(map(lambda a: a.mining_fee, last_block.tnxs))
            rs.blocks[last_block.hash] = last_block



        rs2 = RemoteState()
        for commit in s.repo.iter_commits(f"..{recent_common_commit}"):

            if last_block is None:
                if match_block(commit.message) is not None:
                    last_block = Block.from_commit(commit)
                else:
                    rs2.mempool.append(TnxInfo.from_str(commit.message))
                continue

            if match_block(commit.message) is not None:
                last_block.worth = sum(map(lambda a: a.mining_fee, last_block.tnxs))
                rs2.blocks[commit.hash] = last_block
                last_block = Block.from_commit(commit)
            
            tnx_info = TnxInfo.from_str(commit.message)
            tnx = Tnx(commit.hash, commit.parents[0].hash, tnx_info)
            rs2.tnxs[commit.hash] = tnx
            rs2.last_block.tnxs.append(tnx)

        if last_block is not None:
            rs2.blocks[last_block.hash] = last_block

        # if we have more blocks, we have to reset on that chain
        if len(rs.blocks) > len(rs2.blocks):
            remote_latest_commit = next(s.repo.iter_commits(f"{remote.name}/main")).hash
            s.repo.reset("--hard", remote_latest_commit.hash)

            # remove everything in rs2 form s
            for hash in rs2.tnxs.keys():
                del s.tnxs[hash]
            for hash in rs2.blocks.keys():
                del s.blocks[hash]

            # add everything in rs to s
            for hash, tnx in rs.tnxs.items():
                s.tnxs[hash] = tnx
            for hash, block in rs.blocks.items():
                s.blocks[hash] = tnx

            # try to add anything else we can add
            for tnx in rs2.tnxs.values():
                if validate_tnx(tnx, s):
                    commit_transaction(s, tnx)

        # otherwise put everything we can into mempool
        else:
            for tnx in rs.tnxs.values():
                if validate_tnx(tnx, s):
                    commit_transaction(s, tnx)

        
def commit_transaction(s: State, tnx_i: TnxInfo):
    s.repo.git.commit("--empty-commit", "-m", f"\"{str(tnx_i)}\"")
    commit = next(s.repo.iter_commits())
    tnx = Tnx.from_info(commit.hash, commit.parent[0].hash, tnx_i)
    s.tnxs[tnx.hash] = tnx
