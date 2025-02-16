from gitcoin.logic import State, Tnx, TnxInfo, validate_tnx, Block, init_chain
from unittest.mock import patch
from git import Repo, Commit
from git.util import bin_to_hex
b2x=lambda b: bin_to_hex(b).decode("ascii")


def test_validate_tnx_simple():
    s = State({}, [], None, None, None, None)

    tnx_1 = Tnx("pubkey1", [], {"pubkey2": 10}, 1, "sig", "TNX1", "eep")
    s.tnxs[tnx_1.hash] = tnx_1

    #wrong amount
    tnx_2_fail = Tnx("pubkey2", ["TNX1"], {"pubkey3": 1}, 1, "sig", "TNX2", "eep")
    assert not validate_tnx(tnx_2_fail, s)

    #should work
    tnx_2 = Tnx("pubkey2", ["TNX1"], {"pubkey3": 9}, 1, "sig", "TNX2", "eep")
    assert validate_tnx(tnx_2, s)
    s.tnxs[tnx_2.hash] = tnx_2

    #source seen should fail 
    tnx_2 = Tnx("pub", ["TNX1"], {"pubkey3": 9}, 1, "sig", "TNX2", "eep")
    assert not validate_tnx(tnx_2, s)


"""
def test_tnxinfo_validate_signed():
    signed = TnxInfo.sign("b2313d6d", "65a7ddd982a132bf", ["src1", "src2"], {"dest1": 5, "dest2": 10}, 15)
    assert signed.validate()


def test_tnxinfo_serialize_deserialize():
    tnxi = TnxInfo("pub1", ["src1", "src2"], {"dest1": 1, "dest2": 2}, 3, "sign")
    tnxi_str = str(tnxi)
    tnix_str_tnxi = TnxInfo.from_str(tnxi_str)
    assert tnxi == tnix_str_tnxi

    
def test_init_chain():

    c1 = Commit("", b"00000000000000000000", message=str(TnxInfo("nothing", ["nothing"], {"pub1": 10}, 0, "sign")), parents=[])
    c2 = Commit("", b"00000000000000000001", message=str(Block("header", "pub1", 10, [b2x(b"00000000000000000000")])), parents=[c1])
    c3 = Commit("", b"00000000000000000002", message=str(TnxInfo("pub1", [b2x(b"00000000000000000000")], {"pub2": 10}, 0, "sign")), parents=[c2])
    c4 = Commit("", b"00000000000000000003", message=str(TnxInfo("pub1", [b2x(b"00000000000000000001")], {"pub3": 10}, 0, "sign")), parents=[c3])
    
    with patch.object(Repo, "iter_commits", return_value=[c4, c3, c2, c1]): 
        state = State({}, [], {}, Repo("."), None, None)
        init_chain(state)

    assert len(state.blocks) == 1
    assert len(state.tnxs) == 2
    assert len(state.mempool) == 1

    

def test_rebase_on_remotes_add_tnxs():
    pass


def test_rebase_on_remotes_reset():
    pass
"""
