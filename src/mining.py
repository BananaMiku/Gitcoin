from datetime import datetime
from threading import Thread

def mine():

    last_time = datetime.now()
    block_header = None
    chain = get_transactions()

    while block_header is None:

        for _ in range(1000):
            block_header = try_find_block_hash()
            if block_header is not None: break

        if (last_time - datetime.now()).total_seconds() > 10:
            last_time = datetime.now()
            thread = Thread(target=rebase_on_remotes, args=chain)
            thread.start()

    append_block(block_header)


    
    



