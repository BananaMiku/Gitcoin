from datetime import datetime
from threading import Thread

def mine():

    pitched = get_pitched()
    append_pitched(pitched)

    last_time = datetime.now()
    found_block_hash = False
    chain = get_transactions()

    while not found_block_hash:

        for _ in range(1000):
            found_block_hash = try_find_block_hash()
            if found_block_hash: break

        if (last_time - datetime.now()).total_seconds() > 10:
            last_time = datetime.now()
            thread = Thread(target=update_chain_thread, args=chain)
            thread.start()
    


def update_chain_thread(chain):
    for remote in get_remotes():
        rebase_on(remote)
    
    



