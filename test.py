from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
import os

print("Random test:", os.urandom(16).hex())

# -------------------------------
# 1. Generate Keys and Sign a Message
# -------------------------------

# Generate RSA private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Extract the public key
public_key = private_key.public_key()

# Serialize the private key to PEM format (bytes) and then decode to a string
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
private_pem_str = private_pem.decode()

# Serialize the public key to PEM format (bytes) and then decode to a string
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
public_pem_str = public_pem.decode()

print("Private Key PEM String:\n", private_pem_str)
print("Public Key PEM String:\n", public_pem_str)

# Message to be signed
message = b"Hello, this is a signed message."

# Sign the message using the private key

# Convert the private key PEM string back to a private key object
loaded_private_key = load_pem_private_key(
    private_pem_str.encode(),  # convert back to bytes
    password=None
)


signature = loaded_private_key.sign(
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Convert signature bytes to a hexadecimal string for display/storage
signature_hex = signature.hex()
print("Signature (hex):", signature_hex)

# -------------------------------
# 2. Convert PEM Strings Back to Key Objects
# -------------------------------


# Convert the public key PEM string back to a public key object
loaded_public_key = load_pem_public_key(
    public_pem_str.encode()  # convert back to bytes
)

# -------------------------------
# 3. Convert Hex Signature Back to Bytes and Verify
# -------------------------------

# Convert the hexadecimal signature string back into bytes
signature_bytes = bytes.fromhex(signature_hex)

# Verify the signature using the loaded public key
try:
    loaded_public_key.verify(
        signature_bytes,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("Signature verification successful!")
except Exception as e:
    print("Signature verification failed:", e)
