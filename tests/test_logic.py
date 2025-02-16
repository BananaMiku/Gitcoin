from gitcoin.logic import State, Tnx, TnxInfo, validate_tnx, Block
from unittest.mock import patch
from git import Repo, Commit
from git.util import bin_to_hex
b2h=lambda b: bin_to_hex(b).decode(ascii)


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
    signed = TnxInfo.sign("privkey", "pubkey", ["src1", "src2"], {"dest1": 5, "dest2": 10}, 15)
    assert signed.validate()


def test_tnxinfo_serialize_deserialize():
    tnxi = TnxInfo("pub1", ["src1", "src2"], {"dest1": 1, "dest2": 2}, 3, "sign")
    tnxi_str = str(tnxi)
    tnix_str_tnxi = TnxInfo.from_str(tnxi_str)
    assert tnxi == tnix_str_tnxi

    
def test_init_chain():
    with patch.object(Repo, "iter_commits", return_value=[
            Commit("", b"00000000000000000000", message=str(TnxInfo("nothing", ["nothing"], {"pub1": 10}, 0, "sign"))),
            Commit("", b"00000000000000000001", message=str(Block("", "pub1", 10, [b2x(b"00000000000000000000")]))),
            Commit("", b"00000000000000000002", message=str(TnxInfo("pub1", [b2x(b"00000000000000000000")], 0, "sign"))),
        ]):

        state = State({}, [], {}, None, None, None)
        init_chain(state)


    assert len(state.blocks) == 1
    # TODO: test omre
    

def test_rebase_on_remotes_add_tnxs():
    pass


def test_rebase_on_remotes_reset():
    pass
"""
