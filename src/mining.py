from datetime import datetime
from threading import Thread
from logic import State, 

def mine(state: State):

    last_time = datetime.now()
    block_header = None

    while block_header is None:

        for _ in range(1000):
            block_header = try_find_block_hash()
            if block_header is not None: break

        if (last_time - datetime.now()).total_seconds() > 10:
            last_time = datetime.now()
            thread = Thread(target=rebase_on_remotes, args=state)
            thread.start()

    append_block(state, block_header)


    
    



