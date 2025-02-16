import random
import hashlib
from gitcoin.logic import State, Tnx, TnxInfo

def generate_large_prime(bits=32):
    import sympy
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
        
def get_balance(self, state: State) -> int:
    """Calculates available balance based on previous transactions in the state."""
    total_balance = 0

    # Calculate balance from source transactions
    for tnx in state.tnxs.values():
        if tnx.pubkey == self.pubkey:
            total_balance += sum(tnx.dests.values())  # Total funds sent to others
            total_balance -= tnx.mining_fee  # Account for any fees

    return total_balance

def make_transaction(state: State, dest_list: list[tuple[str, int]], fee: int):
    '''
    pubkey: The public key of the user (string)
    privkey: The private key of the user (string)
    state: from logic.py, State class
    dest_list: list of tuples, each tuple is of the form (receiver, amount)
    fee: cost for making the transaction
    balance: Current balance of the user
    '''

    # Calculate the total amount to be sent
    total_amount = sum(amount for _, amount in dest_list)

    # Start with the transaction fee
    total_spent = fee
    srcs = []  # Keep track of sources used in the transaction

    # Gather all previously used sources
    used_sources = set()
    for tnx in state.tnxs.values():
        used_sources.update(tnx.srcs)

    # Validate that sufficient funds are available
    for dest_pubkey, amount in dest_list:
        if amount <= 0:
            raise ValueError(f"Transaction amount cannot be negative for destination {dest_pubkey}.")
        total_spent += amount

    # Calculate how much the given person has
    for hash, tnx in state.tnxs.items():
        bad = True
        for tnx_ in tnx.dests:
            if tnx_[0] == state.pubkey:
                bad = False
                for hash_temp, tnx_temp in state.tnxs.items():
                    if hash in tnx_temp.srcs:
                        bad = True
                        break
                if bad:
                    continue

                srcs.append(tnx.hash)
                total_spent -= tnx_[1]
    
    for hash, block in state.blocks.items():
        if block.owner==state.pubkey:
            bad = False
            for hash_temp, tnx_temp in state.tnxs.items():
                if hash in tnx_temp.srcs:
                    bad = True
                    break
            if bad:
                continue
            srcs.append(hash)
            total_spent -= block.worth

    # Create a new transaction info object
    dest_dict = {dest_pubkey: amount for dest_pubkey, amount in dest_list}
    if total_spent > 0:
        raise ValueError(f"Total Spent should not be positive.")

    return TnxInfo.sign(state.privkey, state.pubkey, srcs, dest_dict, fee)

def get_balance(self, user):
    """Returns the balance of the user."""
    return self.balances.get(user.user_id, 0)

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