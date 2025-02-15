import gitcoin.logic

def test_validate_tnx_simple():
    #makes a state
    s = logic.State({}, [], None, None, None)

    #adds to the state
    #return Tnx(info.pubkey, info.srcs, info.dests, info.mining_fee, info.signature, hash, prev_hash)
    tnx_1 = logic.Tnx("pubkey1", [], {"pubkey2": 10}, 1, "sig", "TNX1", "eep")
    s.tnxs[tnx_1.hash] = tnx_1
    tnx_2 = logic.Tnx("pubkey2", ["TNX1"], {"pubkey3": 9}, 1, "sig", "TNX2", "eep")
    assert logic.validate_tnx(tnx_2, s)

