from dataclasses import dataclass
from git import Repo

@dataclass
class State:
    tnx: Tnx
    repo: Repo

class Tnx:
    def __init__(self, hash_, prev_hash_, id, dests_, amnts_, mine_fee):
        self.hash = hash_
        self.prev_hash = prev_hash_ 
        self.id
        self.dests = dests_ #dests 
        self.amnts = amnts_ #amounts per dest 
        self.mine_fee = mine_fee

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

def init_tnx_map(state):
    map = {}
    pass

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
