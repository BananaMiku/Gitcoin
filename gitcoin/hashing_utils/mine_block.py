import os
import subprocess
import zlib
import hashlib
from gitcoin.hashing_utils import mine_cpu

def mine(search_limit):
    """ Tries to mine a block and pushes it to the current branch.
    
    If a block is mined successfully, then it is committed to the current branch and the function returns True.
    Otherwise, this function returns False.
    """
    default_commit_message = 'pubkey\n\n00000000000000000000000000000000'

    subprocess.run(['git', 'commit', '--allow-empty', '-m', default_commit_message, '--no-gpg-sign'])
    
    commit_hash = subprocess.run(['git', 'log'], capture_output=True).stdout.decode('utf-8')
    commit_hash = commit_hash.split('\n')[0]
    commit_hash = commit_hash.split(' ')[1]
    
    commit_data = subprocess.run(['git', 'cat-file', '-p', commit_hash], capture_output=True).stdout
    
    commit_block = b'commit ' + str(len(commit_data)).encode('ascii') + b'\0' + commit_data
    
    subprocess.run(['git', 'reset', 'HEAD~1'])

    solution = mine_cpu.mine(commit_block, search_limit)
    if solution == None:
        return False
    
    solution_hash = hashlib.sha1(solution).hexdigest()
    
    compressed_solution_data = zlib.compress(solution)
    
    os.makedirs('.git/objects/{solution_hash[:2]}', exist_ok=True)
    
    with open(f'.git/objects/{solution_hash[:2]}/{solution_hash[2:]}', 'wb+') as odb_entry:
        odb_entry.write(compressed_solution_data)
    
    subprocess.run(['git', 'reset', solution_hash])
    return True

if __name__ == '__main__':
    mine(0x10000)
