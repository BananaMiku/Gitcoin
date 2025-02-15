class tnx:
    def __init__(self, hash_, prev_hash_, dests_, sources_):
        self.hash = hash_
        self.prev_hash = prev_hash_
        self.dests = dests_
        self.sources = sources_ #list of tnx hashes

def validate_tnx(to_validate: tnx, tnx_set):
    assert(tnx != NULL)
    for source in tnx.sources:
        amt = 0 
        for 



def gen_block():
    pass

def validate_block():
    pass


