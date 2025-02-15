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


def validate_tnx(to_validate: Tnx, s: State):
    #tnx should exist
    if to_validate == NULL:
        return False

    #source should exist
    for src in to_validate.srcs:
        if src not in s.tnxs:
            return False

    #amnts should be the same
    amnt_to_spend = to_validate.mine_fee 
    for dest in to_validate.dests:
        if to_validate.dests[dest] < 0:
            return False

        amnt_to_spend += to_validate.dests[dest]

    
    for src in to_validate.srcs:
        src_tnx = s.tnxs[src]
        if to_validate.pubkey not in src_tnx.dests:
            return False 
        amnt_to_spend -= src.dests[to_validate.pubkey]

    if amnt_to_spend != 0:
        return False


    #no other tnx should point to the same
    for hash in s.tnxs:
        if s.tnxs[hash].pubkey != to_validate.pubkey:
            continue

        for src in s.tnx[hash].srcs:
            if src in to_validate.srcs:
                return False


    #tnx is good
    return True


def check_sig(sig):
    return True

#validates block and updates tnx_map
def validate_block(added_tnxs, s):
    for i, tnx in enumerate(added_tnx):
        if not validate_tnx(tnx, s):
            #clears everything we added
            for j in range(i):
                del s.tnxs[added_tnx[j].hash]

            return False
        s.tnxs[tnx.hash] = tnx

    return True


def construct_tnxs(state: State):
    """constructs the commit hash -> Tnx map from the repo"""

    state.tnxs = {}
    seen_block = False
    for commit in state.repo.iter_commits():

        # we only care about everything after the most recent block
        if not seen_block:
            if match_block(commit.message) is not None:
                seen_block = True

            continue

        
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
