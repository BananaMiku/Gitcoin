import logic

def run_all_tests():
    validate_tnx_test()

def validate_tnx_test():
    print("Running Validate TNX Test -----")
    #makes a state
    s = logic.State({}, [], None, None, None)

    #adds to the state
    #return Tnx(info.pubkey, info.srcs, info.dests, info.mining_fee, info.signature, hash, prev_hash)
    tnx_1 = logic.Tnx("pubkey1", [], {"pubkey2": 10}, 1, "sig", "TNX1", "eep")
    s.tnxs[tnx_1.hash] = tnx_1
    print(s)
    tnx_2 = logic.Tnx("pubkey2", ["TNX1"], {"pubkey3": 9}, 1, "sig", "TNX2", "eep")
    print (f"adding 1 valid tnx works: {logic.validate_tnx(tnx_2, s)}")


if __name__ == "__main__":
    run_all_tests()
