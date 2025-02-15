from dataclasses import dataclass, field
from git import Repo, Commit
import re

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
    tnxs: list[Tnx] = field(default_factory=list)


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


def check_sig(sig):
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
                last_block = Block(commit.hash)

            else:
                state.mempool.append(TnxInfo.from_str(commit.message))

            continue

        assert len(commit.parents) == 1 # you can have multiple parents in a merge, we should never have a merge
    
        # if we're a block, ignore
        if match_block(commit.message) is not None:
            state.blocks[commit.hash] = last_block
            last_block = Block(commit.hash)

        tnx_info = TnxInfo.from_str(commit.message)
        tnx = Tnx.from_info(commit.hash, commit.parents[0], tnx_info)
        state.tnxs[tnx.hash] = tnx
        last_block.tnxs.append(tnx)

    state.blocks[last_block.hash] = last_block


def match_block(s: str) -> re.Match:
    return re.match(r"(\w+)\n\n(\w+)", s)

def match_transaction(s: str) -> re.Match:
    return re.match(r"(\w+)\n\n((?:\w+\n)+)((?:\d+ \w+\n)+)(\d)\n(\w+)", s)


def append_block(s: State, header: str):
    """appends a block with a given header"""
    s.repo.git.commit("--empty-commit", "-m", f"{header}\n\n{s.pubkey}")
    # TODO: validate the amount of zeros
    # TODO: make the amount of zeros required depend on how long it took to make the last block


def rebase_on_remotes(s: State) -> list[str]:
    """
    updates the chain based on the remotes
    adds all valid pending transactions the other chains have

    if a longer, valid chain is found, reset to that chain and add
    all pending transactions not on that chain after
    """
    block_set = set(map(lambda a: a.hash, s.blocks))
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
                    last_block = Block(commit.hash)
                else:
                    rs.mempool.append(TnxInfo.from_str(commit.message))
                continue

            if match_block(commit.message) is not None:
                rs.blocks[commit.hash] = last_block
                last_block = Block(commit.hash)
            
            tnx_info = TnxInfo.from_str(commit.message)
            tnx = Tnx(commit.hash, commit.parents[0].hash, tnx_info)
            rs.tnxs[commit.hash] = tnx
            rs.last_block.tnxs.append(tnx)

        if last_block is not None:
            rs.blocks[last_block.hash] = last_block



        rs2 = RemoteState()
        # TODO: finish



        
    
