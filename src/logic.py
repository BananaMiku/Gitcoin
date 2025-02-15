from dataclasses import dataclass
from git import Repo
import re

@dataclass
class State:
    tnxs: dict[str, Tnx]
    repo: Repo

@dataclass
class Tnx:
    # hash is the commit hash
    hash: str

    # prev_hash is the hash of the previous commit
    prev_hash: str

    # pubkey is the public key of the user sending the money
    pubkey: str

    # srcs is a list of sources for transactions
    srcs: list[src]

    # map from destination public key to amount to send
    dests: dict[str, int]

    # fee allocated to the miner
    mining_fee: int

    # signature
    signature: str


def validate_tnx(to_validate: Tnx, tnx_map):
    #tnx should exist
    if tnx == NULL:
        return False

    if len(tnx.dests) != len(tnx.amnts):
        return False

    #source should exist
    if tnx.prev_hash not in tnx_map:
        return False; 

    #amnts should be the same
    amnt_to_spend = tnx.mine_fee 
    for amount in tnx.amnts:
        amnt_to_spend += amount

    source = tnx_map[tnx.prev_hash]
    try:
        amnt_index = source.dests.index(id)
        if sources.amnts[amnt_index] != amnt_to_spend:
            return False 
    except:
        return False

    if amnt_to_spend != amnt_can_spend:
        return False

    #no other tnx should point to source
    for hash in tnx_map:
        if tnx_map[hash].prev_hash == tnx.prev_hash:
            return False
    return True


#validates block and updates tnx_map
def validate_block(tnxs_in_block, tnx_map):
    for i, tnx in enumerate(tnxs_in_block):
        if not validate_tnx(tnx, tnx_map):
            #clears everything we added
            for j in range(i):
                del tnx_map[tnx.hash]

            return False
        tnx_map[tnx.hash] = tnx

    return True


def construct_tnxs(state: State):
    """constructs the commit hash -> Tnx map from the repo"""

    state.tnxs = {}
    for commit in state.repo.iter_commits():
        
        assert len(commit.parents) == 1 # you can have multiple parents in a merge, we should never have a merge
        
        # if we're a block, ignore
        if match_block(commit.message) is not None:
            continue
                
        tnx_match = match_transaction(commit.message)
        assert tnx_match is not None
        assert len(tnx_match.groups()) == 5

        [pubkey, srcs_raw, dests_raw, fee, signature] = tnx_match.groups()
        srcs = srcs_raw.split("\n")
        dests = {pubkey: int(amount) for [amount, pubkey] in map(lambda a: a.split(" "), dests_raw.split("\n"))}
        
        tnx = Tnx(commit.hash, commit.parents[0], pubkey, srcs, dests, int(fee), signature)
        state.tnxs[tnx.hash] = tnx


def match_block(s: str) -> re.Match:
    return re.match("(\w+)\n\n(\w+)", s)

def match_transaction(s: str) -> re.Match:
    return re.match("(\w+)\n\n((?:\w+\n)+)((?:\d+ \w+\n)+)(\d)\n(\w+)", s)


def update_tnx_map():
    pass


def append_block(s: State, header: str):
    """appends a block with a given header"""
    s.repo.git.commit("--empty-commit", "-m", header)
    # TODO: validate the amount of zeros
    # TODO: make the amount of zeros required depend on how long it took to make the last block


def rebase_on_remotes(s: State) -> list[str]:
    """
    updates the chain based on the remotes
    adds all valid pending transactions the other chains have

    if a longer, valid chain is found, reset to that chain and add
    all pending transactions not on that chain after
    """
    remotes = s.repo.remote()
