import os
import subprocess
import zlib
import hashlib
import mine_cpu

def mine():
    # blank 128 bit nonce
    message = 'pubkey\n\n00000000000000000000000000000000'
    subprocess.run(['git', 'commit', '--allow-empty', '--allow-empty-message', '-m', message, '--no-gpg-sign'])
    
    commit_id = subprocess.run(['git', 'log'], capture_output=True).stdout.decode('utf-8')
    commit_id = commit_id.split('\n')[0]
    commit_id = commit_id.split(' ')[1]
    
    # print(commit_id)
    
    commit_block = subprocess.run(['git', 'cat-file', '-p', commit_id], capture_output=True).stdout
    
    # print(commit_block)
    
    commit_data = b'commit ' + str(len(commit_block)).encode('ascii') + b'\0' + commit_block
    
    # print(commit_data)
    
    solution = mine_cpu.mine(commit_data)
    
    commit_hash = hashlib.sha1(solution).hexdigest()
    
    compressed_solution_data = zlib.compress(solution)
    
    os.makedirs('.git/objects/{commit_hash[:2]}', exist_ok=True)
    
    with open(f'.git/objects/{commit_hash[:2]}/{commit_hash[2:]}', 'wb+') as odb_entry:
        odb_entry.write(compressed_solution_data)
    
    subprocess.run(['git', 'reset', commit_hash])

if __name__ == '__main__':
    mine()
