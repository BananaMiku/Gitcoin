"""
from gitcoin.logic import State, Tnx, TnxInfo
from gitcoin.transact import make_transaction
def test_transaction_simple():
    s = State([], {}, [], None, "priv1", "pub1")
    s.tnxs["hash1"] = Tnx("nothing", ["nothing"], ["pub1", 10], 0, None, "hash1", None)

    tnx: TnxInfo = make_transaction(s, {"pub2": 8}, 2)
    assert tnx.pubkey == "pub1"
    assert tnx.srcs == ["hash1"]
    assert tnx.dests == {"pub2": 8}
    assert tnx.mining_fee == 2


def test_coinbase_transaction_simple():
    s = State([], {}, [], None, "priv1", "pub1")
    s.blocks["hash1"] = Block("hash1", "pub1", 10)

    tnx: TnxInfo = make_transaction(s, {"pub2": 8}, 2)
    assert tnx.pubkey == "pub1"
    assert tnx.srcs == ["hash1"]
    assert tnx.dests == {"pub2": 8}
    assert tnx.mining_fee == 2


def test_transaction_already_used():
    s = State([], {}, [], None, "priv1", "pub1")
    s.tnxs["hash1"] = Tnx("nothing", ["nothing"], ["pub1", 10], 0, None, "hash1", None)
    s.tnxs["hash2"] = Tnx("pub1", ["hash1"], ["pub2", 10], 0, None, "hash2", None)

    try:
        tnx: TnxInfo = make_transaction(s, {"pub2": 8}, 2)
        assert False, f"didn't throw exception: {tnx}"

    except ValueError:
        pass





    

"""
