from gitcoin.logic import State, Tnx, TnxInfo
from gitcoin.transact import make_transaction
from gitcoin.utils import pem_to_simple

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



def test_transaction_simple():
    s = State({}, [], {}, None, pub, priv)
    s.tnxs["hash1"] = Tnx("nothing", ["nothing"], [pub, 10], 0, None, "hash1", None)

    tnx: TnxInfo = make_transaction(s, [["pub2", 8]], 2)
    assert tnx.pubkey == pub
    assert tnx.srcs == ["hash1"]
    assert tnx.dests == {"pub2": 8}
    assert tnx.mining_fee == 2
    assert tnx.verify()


def test_coinbase_transaction_simple():
    s = State({}, [], {}, None, pub, priv)
    s.blocks["hash1"] = Block("hash1", pub, 10)

    tnx: TnxInfo = make_transaction(s, [["pub2", 8]], 2)
    assert tnx.pubkey == pub
    assert tnx.srcs == ["hash1"]
    assert tnx.dests == {"pub2": 8}
    assert tnx.mining_fee == 2


def test_transaction_already_used():
    s = State({}, [], {}, None, pub, priv)
    s.tnxs["hash1"] = Tnx("nothing", ["nothing"], [pub, 10], 0, None, "hash1", None)
    s.tnxs["hash2"] = Tnx(pub, ["hash1"], ["pub2", 10], 0, None, "hash2", None)

    try:
        tnx: TnxInfo = make_transaction(s, [["pub2", 8]], 2)
        assert False, f"didn't throw exception: {tnx}"

    except ValueError:
        pass


def test_transaction_excess():
    s = State({}, [], {}, None, pub, priv)
    s.tnxs["hash1"] = Tnx("nothing", ["nothing"], [pub, 10], 0, None, "hash1", None)

    tnx: TnxInfo = make_transaction(s, [["pub2", 6]], 2)
    assert tnx.pubkey == pub
    assert tnx.srcs == ["hash1"]
    assert tnx.dests["pub2"] == 6
    assert tnx.dests[pub] == 2 # excess
    assert tnx.mining_fee == 2
    assert tnx.validate()

    
def test_transaction_nightmare():
    s = State({}, [], {}, None, pub, priv)
    s.tnxs["hash1"] = Tnx("nothing", ["nothing"], [pub, 10], 0, None, "hash1", None)
    s.tnxs["hash2"] = Tnx(pub, ["hash1"], ["pub2", 10], 0, None, "hash2", None)
    s.blocks["hash3"] = Block("hash1", pub, 10)
    s.tnxs["hash5"] = Tnx("nothing", ["nothing"], [pub, 10], 0, None, "hash1", None)

    tnx: TnxInfo = make_transaction(s, [["pub2", 15]], 0)
    assert tnx.pubkey == pub
    assert set(tnx.srcs) == set(["hash3", "hash5"])
    assert tnx.dests["pub2"] == 15
    assert tnx.dests[pub] == 5
    assert tnx.mining_fee == 0
    assert tnx.validate()




    

