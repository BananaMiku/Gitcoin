from gitcoin.logic import State, Tnx, TnxInfo, validate_tnx

def test_validate_tnx_simple():
    #makes a state
    s = State({}, [], None, None, None, None)

    #adds to the state
    #return Tnx(info.pubkey, info.srcs, info.dests, info.mining_fee, info.signature, hash, prev_hash)
    tnx_1 = Tnx("pubkey1", [], {"pubkey2": 10}, 1, "sig", "TNX1", "eep")
    s.tnxs[tnx_1.hash] = tnx_1
    tnx_2 = Tnx("pubkey2", ["TNX1"], {"pubkey3": 9}, 1, "sig", "TNX2", "eep")
    assert validate_tnx(tnx_2, s)


def test_validate_signed_tnxinfo():
    signed = TnxInfo.sign("privkey", "pubkey", ["src1", "src2"], {"dest1": 5, "dest2": 10}, 15)
    assert signed.validate()
