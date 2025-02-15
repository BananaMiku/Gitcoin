import random
import sympy
import hashlib

def generate_large_prime(bits=32):
    """Generates a random large prime number with the given bit size."""
    return sympy.randprime(2**(bits-1), 2**bits)

# Global constants for encryption
G = 3  # Generator
N = 2**64 - 59  # Large prime modulus (can be adjusted)

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.private_prime = generate_large_prime()
        self.public_key = pow(G, self.private_prime, N)  # g^p mod N
        self.value = 0
        
    def compute_valid_private_key(user):
        """
        Computes a valid hashed representation of the user's private key
        using the private prime and public key.
        
        Parameters:
        user (User): A User object containing private prime and public key.
        
        Returns:
        str: The hashed value of the private key.
        """

        # Create a string combining the user's private prime and public key
        # This assumes that `private_prime` is the user's private key.
        valid_input = f"{user.private_prime}{user.public_key}".encode()
        
        # Return the SHA-256 hash of the combined string
        return hashlib.sha256(valid_input).hexdigest()
    
    def make_transaction(self, sender, recipient, amount, private_key):
        """Verifies a user and processes a transaction."""
        
        # Hash the sender's public key and private key, using SHA-256 for a secure hash
        hash_input = f"{private_key}{sender.public_key}".encode()
        hashed_key = hashlib.sha256(hash_input).hexdigest()

        #verify this hashed_key against a stored hash
        valid_private_key = self.compute_valid_private_key(sender)  # Placeholder for actual check

        if hashed_key == valid_private_key:
            if sender.value > amount:
                print(f"Transaction from {sender.user_id} to {recipient.user_id} for {amount} is valid.")
                sender.value -= amount
                recipient.value += amount
                return True
            else:
                print("Sender does not have adequate funds")
                return False
        else:
            print("Invalid private key. Transaction failed.")
            return False

