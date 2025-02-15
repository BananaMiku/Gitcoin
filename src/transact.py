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

    def compute_valid_private_key(self):
        """Computes a valid hashed representation of the user's private key."""
        valid_input = f"{self.private_prime}{self.public_key}".encode()
        return hashlib.sha256(valid_input).hexdigest()

class Bank:
    def __init__(self):
        self.balances = {}  # Dictionary to hold user balances

    def create_account(self, user):
        """Creates an account for the user with an initial balance of 0."""
        self.balances[user.user_id] = 0

    def get_balance(self, user):
        """Returns the balance of the user."""
        return self.balances.get(user.user_id, 0)

    def update_balance(self, user, amount):
        """Updates the balance for the user."""
        if user.user_id in self.balances:
            self.balances[user.user_id] += amount

    def make_transaction(self, sender, recipient, amount, private_key):
        """Verifies a user and processes a transaction."""
        # Hash the sender's private key and public key using SHA-256 for a secure hash
        hash_input = f"{private_key}{sender.public_key}".encode()
        hashed_key = hashlib.sha256(hash_input).hexdigest()

        # Verify this hashed_key against a stored hash
        valid_private_key = sender.compute_valid_private_key()

        if hashed_key == valid_private_key:
            # Check if the sender has enough funds
            if self.get_balance(sender) >= amount:
                print(f"Transaction from {sender.user_id} to {recipient.user_id} for {amount} is valid.")
                self.update_balance(sender, -amount)
                self.update_balance(recipient, amount)
                return True
            else:
                print("Sender does not have adequate funds")
                return False
        else:
            print("Invalid private key. Transaction failed.")
            return False

# Example of usage
user1 = User("user1")
user2 = User("user2")

bank = Bank()
bank.create_account(user1)
bank.create_account(user2)

# Setting initial balances for demonstration purposes
bank.update_balance(user1, 100)  # Giving user1 initial balance

# Attempting a transaction
print(bank.balances)
bank.make_transaction(user1, user2, 50, user1.private_prime)
print(bank.balances)