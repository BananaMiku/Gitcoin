import os
import subprocess
import zlib
import hashlib
from git import Repo
from gitcoin.logic import State
from gitcoin.hashing_utils import mine_cpu

def mine(search_limit, state: State):
    """ Tries to mine a block and pushes it to the current branch.
    
    If a block is mined successfully, then it is committed to the current branch and the function returns True.
    Otherwise, this function returns False.
    """

    repo = state.repo

    old_commit_hash = repo.head.commit.hexsha
    default_commit_message = f'{state.pubkey}\n\n00000000000000000000000000000000'

    try:
        repo.git.commit('--allow-empty', '-m', default_commit_message, '--no-gpg-sign', '-q')
        
        commit_hash = repo.head.commit.hexsha
        
        commit_data = repo.git.cat_file('-p', commit_hash)
        
        commit_block = b'commit ' + str(len(commit_data)).encode('ascii') + b'\0' + commit_data.encode('ascii')
    finally:
        repo.git.reset(old_commit_hash)

    solution = mine_cpu.mine(commit_block, search_limit)
    if solution == None:
        return False
    
    solution_hash = hashlib.sha1(solution).hexdigest()
    
    compressed_solution_data = zlib.compress(solution)
    
    os.makedirs(f'{repo.working_dir}/.git/objects/{solution_hash[:2]}', exist_ok=True)
    
    
    with open(f'{repo.working_dir}/.git/objects/{solution_hash[:2]}/{solution_hash[2:]}', 'wb+') as odb_entry:
        odb_entry.write(compressed_solution_data)
    
    repo.git.reset(solution_hash)
    return True

if __name__ == '__main__':
    mine(0x10000)
