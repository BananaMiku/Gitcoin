from dataclasses import dataclass
from git import Repo

@dataclass
class State:
    tnx: Tnx
    repo: Repo

class Tnx:
    def __init__(self, hash_, prev_hash_, dests_, amnts_):
        self.hash = hash_
        self.prev_hash = prev_hash_ 
        self.dests = dests_ #dests 
        self.amnts = amnts_ #amounts per dest 

def validate_tnx(to_validate: Tnx, tnx_map):
    #tnx should exist
    if tnx == NULL:
        return False

    #source should exist
    if tnx.prev_hash not in tnx_map:
        return False; 

    #amnts should be the same
    amnt_to_spend = 0
    for amount in tnx.amnts:
        amnt_to_spend += amount

    source = tnx_map[tnx.prev_hash]
    amnt_can_spend = 0
    for amount in source.amnts:
        amnt_can_spend += amount

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

def append_block(state, header: str):
    """appends a block with a given header"""


def rebase_on_remotes(state, chain: Tnx) -> list[str]:
    """
    updates the chain based on the remotes
    adds all valid pending transactions the other chains have

    if a longer, valid chain is found, reset to that chain and add
    all pending transactions not on that chain after
    """

