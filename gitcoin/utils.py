

def pem_to_simple(s: str):

    return "".join(s.split("\n")[1:-2])

def simple_to_pem(s: str, priv=True):
    typ = priv and "PRIVATE" or "PUBLIC"
    res = [s[i:i+64] for i in range(0, len(s), 64)]
    res = [f"-----BEGIN {typ} KEY-----"] + res + [f"-----END {typ} KEY-----"]
    return "\n".join(res)



    
    




