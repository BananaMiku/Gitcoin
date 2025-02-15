from datetime import datetime
from threading import Thread

def mine():

    pitched = get_pitched()
    append_pitched(pitched)

    last_time = datetime.now()
    block_header = None
    chain = get_transactions()

    while block_header is None:

        for _ in range(1000):
            block_header = try_find_block_hash()
            if block_header is not None: break

        if (last_time - datetime.now()).total_seconds() > 10:
            last_time = datetime.now()
            thread = Thread(target=update_chain_thread, args=chain)
            thread.start()

    append_block(block_header)


def update_chain_thread(chain):
    for remote in get_remotes():
        rebase_on(remote)
    
    



