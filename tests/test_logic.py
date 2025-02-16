from gitcoin.logic import State, Tnx, TnxInfo, validate_tnx, Block, init_chain
from gitcoin.utils import pem_to_simple
from unittest.mock import patch
from git import Repo, Commit, Git
from git.util import bin_to_hex

import os

import pytest

CLIENT_TEST_DIR = "/home/maxwell/Repositories/git-test/test-client"
TEST_REMOTE = "git@github.com:maxwell3025/test-repo.git"

b2x=lambda b: bin_to_hex(b).decode("ascii")

priv = pem_to_simple("""-----BEGIN PRIVATE KEY-----
MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBALhfts/SuoD6fv+p
azNRZC0RJUE999QUWEFDfuJXZKx+e2k4hQ76pSuw5d9rkQXR43VSoSPGv9Yu7bE5
8jPs2i/BJ6VVeW5pOvaLnjh8Iah+25uOID/2UEseij077KBYWy8GRoxmOZyh4zkW
hJEzmV8STA1JGR1NIafDzteKHKwNAgMBAAECgYALIRvz55CCgJxx6lQiQON/JO3O
xmLTVncNWXmrSAM3tlrUuyitAsw9muwFVIToiQbl6hr4AeNKloKalBjesYlqBjIJ
MPFrhbT51enQuvjeKkm5tXt//FXl7beAxBnVAUN6R5b/ssAD8wbiF+rcP63lMQTY
2CTP3wDnhoA4c6KiAQJBAO7hJLBAAYU6bfzi0sVZp0ap2qQV14UWMsQBdBZG9JGY
rixy1UrcRHYARldNFPmPRUALzr36EzU370FlLDWaqeECQQDFloaqO3dND9XEE8CE
uGZ7wrVRPhUapmfYPdF0r7HJ1bAFfU5rXfI/YChn7GimGVEGqkBKj6MViH1FmZ+w
+b+tAkEAwmhIy4fLtPmQeba/gg0srb2eStvbwlwGhK4KI/crIzL2zQXHwFzy+nXO
yU3aPB/1Y+I4JzRWXYFgHgCQsi9lAQJBAINOJO+71OxBOa2z8pxAbtqP6i6zMxMi
wp/RdQA2Qc//UZpUS2jOZc33+OIXGPRInq/vNApYqegFbDp0fMr/LYECQFOW09JB
1ddTvlpU4zyV8S1dM8lIQseyXcu5RAzmrJmkuStwhmUqU8tlPBazGRm/eGH2eMSA
a3Mb1kV9zd2d7Is=
-----END PRIVATE KEY-----
""")
pub = pem_to_simple("""-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC4X7bP0rqA+n7/qWszUWQtESVB
PffUFFhBQ37iV2SsfntpOIUO+qUrsOXfa5EF0eN1UqEjxr/WLu2xOfIz7NovwSel
VXluaTr2i544fCGoftubjiA/9lBLHoo9O+ygWFsvBkaMZjmcoeM5FoSRM5lfEkwN
SRkdTSGnw87XihysDQIDAQAB
-----END PUBLIC KEY-----
""")

@pytest.fixture
def git_repo():
    os.system(f"rm -rf {CLIENT_TEST_DIR}")
    os.system(f"mkdir {CLIENT_TEST_DIR}")
    yield Repo.clone_from(TEST_REMOTE, CLIENT_TEST_DIR)

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


def test_tnxinfo_validate_signed():
    signed = TnxInfo.sign(priv, pub, ["src1", "src2"], {"dest1": 5, "dest2": 10}, 15)
    assert signed.validate()


def test_tnxinfo_serialize_deserialize():
    tnxi = TnxInfo("pub1", ["src1", "src2"], {"dest1": 1, "dest2": 2}, 3, "sign")
    tnxi_str = str(tnxi)
    tnix_str_tnxi = TnxInfo.from_str(tnxi_str)
    assert tnxi == tnix_str_tnxi

    
def test_init_chain(git_repo):
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
