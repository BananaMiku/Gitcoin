class tnx:
    def __init__(self, hash_, prev_hash_, dests_, amnts_):
        self.hash = hash_
        self.prev_hash = prev_hash_ 
        self.dests = dests_ #dests 
        self.amnts = amnts_ #amounts per dest 

def validate_tnx(to_validate: tnx, tnx_set):
    if tnx == NULL:
        return False

    amnt_to_spend = 0
    for amount in tnx.amnts:
        amnt_to_spend += amount

    if tnx.prev_hash not in tnx_set:
        return False; #source should exist

    source = tnx_set[tnx.prev_hash]
    amnt_can_spend = 0
    for amount in source.
    #make sure nothing else is pointing to source 




def gen_block():
    pass

def validate_block():
    pass


