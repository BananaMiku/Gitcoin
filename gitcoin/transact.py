import random
import sympy
import hashlib
from logic import State, Tnx, TnxInfo

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
        
    def get_balance(self, state: State) -> int:
        """Calculates available balance based on previous transactions in the state."""
        total_balance = 0

        # Calculate balance from source transactions
        for tnx in state.tnxs.values():
            if tnx.pubkey == self.pubkey:
                total_balance += sum(tnx.dests.values())  # Total funds sent to others
                total_balance -= tnx.mining_fee  # Account for any fees

        return total_balance

    def make_transaction(self, state, dest_list, fee):
        '''
        state: form logic.py, State class
        dest_list: list of tuples, each tuple is of the form (reciever, amount)
        fee: cost for making transaction
        '''
        # Calculate the total amount to be sent
        total_amount = sum(amount for _, amount in dest_list)

        # Start with the transaction fee
        total_spent = fee  
        srcs = []  # Keep track of sources used in the transaction

        # Validate that sufficient funds are available
        for dest_pubkey, amount in dest_list:
            if amount <= 0:
                raise ValueError(f"Transaction amount cannot be negative for destination {dest_pubkey}.")
            total_spent += amount
        
        # Gather sources and check their availability
        sources_balance = self.get_balance(state)

        #Calculate how much the given person has
        for tnx_hash, tnx in state.tnxs.items():
            if tnx.pubkey == self.pubkey:  # Only consider transactions related to the sender
                srcs.extend(tnx.srcs)
                total_spent -= tnx.dests.get(self.pubkey, 0)

        # If the total amount (+ fee) exceeds the balance, raise an error
        if total_spent > sources_balance:
            raise ValueError("Insufficient funds for the transaction.")
        
        # Create a new transaction info object
        dest_dict = {dest_pubkey: amount for dest_pubkey, amount in dest_list}
        tnx_info = TnxInfo(pubkey=self.pubkey, srcs=srcs, dests=dest_dict, mining_fee=fee, signature='')

        # Create the transaction itself
        new_tnx_hash = 'some_hash_generation_logic'  # This should create a unique hash for the transaction
        new_tnx_prev_hash = 'some_previous_hash_logic'  # Logic to get the last transaction hash or previous state

        transaction = Tnx.from_info(new_tnx_hash, new_tnx_prev_hash, tnx_info)

        # Sign the transaction
        transaction.signature = transaction.sign(self, state.privkey)

        # Update the mempool and the transaction mapping
        state.mempool.append(transaction)
        state.tnxs[transaction.hash] = transaction

        return transaction.hash  # Or return the transaction object if preferred


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