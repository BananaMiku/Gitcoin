# Importing required module
import subprocess
import mine_cpu

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

process = subprocess.Popen(['./mine_cpu'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

process.stdin.write(commit_data)
process.stdin.flush()

print(mine_cpu.mine(4))
