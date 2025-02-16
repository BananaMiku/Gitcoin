import argparse
import subprocess
import json
import os
import random
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import serialization
from gitcoin.animations.miku import task_and_animate
from gitcoin.mining import mine
from git import Repo

from gitcoin.logic import make_keys, State, init_chain, commit_transaction
from gitcoin.utils import pem_to_simple, simple_to_pem
from gitcoin.transact import make_transaction, init_transaction


# only integer transactions are allowed


def dest_and_amt_info(args):
    # join all arguments into a single string
    input = ' '.join(args)
    #print(input)
    try:
        args = input.split(' ')
    except Exception:
        print("Invalid Argument Sequences for 'Pay' command.")

    for i in range(len(args)):
        # even index = destinations
        if i % 2 != 0 and not args[i].isdigit():
            #print(args[i])
            raise TypeError("Amount must be an integer.")

    return args


def run():
    state = State()
    load_state(state) # try to get stuff from state
    if state.repo_location:
        state.repo = Repo(state.repo_location)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", action="store_true", help="raw text, no animations")
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # payment command
    pay_parser = subparsers.add_parser(
        "pay", help="Pay a destination a certain amount of Gitcoin")
    pay_parser.add_argument("dest_and_amt", nargs='+',
                            help="Paying a destination a certain amount of Gitcoin with fees")
    pay_parser.add_argument("-i", action="store_true", help="initial commit, doesnt add sources")

    # subparser for remote command
    remote_parser = subparsers.add_parser("remote", help="git remote clone")
    remote_subparsers = remote_parser.add_subparsers(
        dest="remote_action", help="sub-command help")

    # subparser remote add
    remote_add_parser = remote_subparsers.add_parser(
        "add", help="git remote add clone")
    remote_add_parser.add_argument("name", help="Name of the remote", type=str)
    remote_add_parser.add_argument("url", help="URL of the remote", type=str)

    # subparser remote remove
    remote_remove_parser = remote_subparsers.add_parser(
        "remove", help="git remote remove clone")
    remote_remove_parser.add_argument(
        "name", help="Name of the remote", type=str)

    # mine command
    mine_parser = subparsers.add_parser(
        "mine", help="Mine Gitcoin, with love <3")

    # observer command
    observer_parser = subparsers.add_parser(
        "observer", help="Take a look at your own blockchain")

    keypair_parser = subparsers.add_parser("keypair", help="generate or set keypairs")
    keypair_subparsers = keypair_parser.add_subparsers(dest="keypair_action", help="idk")

    keypair_subparsers.add_parser("gen", help="generate private key")
    keypair_subparsers.add_parser("read", help="read private and public key")
    keypair_set_parser = keypair_subparsers.add_parser("set", help="set your private key")
    keypair_set_parser.add_argument("privkey", help="your private key", type=str)

    repo_parser = subparsers.add_parser("repo", help="get or set repo location")
    repo_subparsers = repo_parser.add_subparsers(dest="repo_action", help="idk")

    repo_subparsers.add_parser("get", help="get repo location")
    repo_set_subparser = repo_subparsers.add_parser("set", help="set your repo location")
    repo_set_subparser.add_argument("location", help="location of your repo", type=str)


    args = parser.parse_args()

    # no input, print help message
    if args.command is None:
        parser.print_help()

    if args.command == "pay":
        if not state.privkey or not state.pubkey:
            raise Exception("Please set your private key (or generate one) before trying to pay people")
        if not state.repo_location:
            raise Exception("Please set the repo for your blockchain")
        
        payment_info = dest_and_amt_info(args.dest_and_amt)
        fee = 1
        if len(payment_info) % 2 != 0:
            fee = payment_info.pop(-1)

        init_chain(state)
        dest_list = [[payment_info[i], int(payment_info[i+1])] for i in range(0, len(payment_info), 2)]
        f = lambda: commit_transaction(make_transaction(state, dest_list, fee))
        if args.i:
            f = lambda: commit_transaction(init_transaction(state, dest_list))

        if args.r:
            f()
        else:
            task_and_animate(random.choice(["plane", "wheel"]), f, (), None, 3)


    elif args.command == "remote":
        print('remote')
        if args.remote_action == "add":
            print(f"Adding remote: {args.name} with URL: {args.url}")
            subprocess.Popen(f'git remote add {args.name} {args.url}', shell=True)
        elif args.remote_action == "remove":
            print(f"Removing remote: {args.name}")
            subprocess.Popen(f'git remote rm {args.name}', shell=True)
        else:
            raise Exception("Invalid remote command")

    elif args.command == "mine":
        if not state.privkey or not state.pubkey:
            raise Exception("Please set your private key (or generate one) before trying to pay people")
        if not state.repo_location:
            raise Exception("Please set the repo for your blockchain")

        if args.r:
            mine(state)
        else:
            task_and_animate(random.choice(["mining", "slots"]), mine, (state,), None, 0)

    elif args.command == "observer":
        print("Observer placeholder")

    elif args.command == "keypair":
        if args.keypair_action == "set":
            with open(args.privkey, "r") as f:
                privkey_pem = f.read()

            public_pem = load_pem_private_key(privkey_pem.encode(), None).public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            print(f"setting private key as follows\n{privkey_pem}")
            state.privkey = pem_to_simple(privkey_pem)
            state.pubkey = pem_to_simple(public_pem)
            
        if args.keypair_action == "gen":
            if state.privkey and state.pubkey:
                raise Exception("This would overwrite your public and private keys, you probably don't wanna do this")
            
            [priv, pub] = make_keys()
            print(f"keys:\n{priv}\n{pub}\n\nthese are saved")
            state.privkey = pem_to_simple(priv)
            state.pubkey = pem_to_simple(pub)
            write_state(state)

        if args.keypair_action == "read":
            if not state.privkey or not state.pubkey:
                raise Exception("No keys yet, generate some ??")
            print(f"keys:\n{simple_to_pem(state.privkey, True)}\n{simple_to_pem(state.pubkey, False)}")

    elif args.command == "repo":
        if args.repo_action == "set":
            state.repo_location = args.location
            state.repo = Repo(args.location)
            print(f"set location to {args.location}")
            write_state(state)

        if args.repo_action == "get":
            if not state.repo_location:
                raise Exception("no repo yet, set it??")

            print(f"location: {state.repo_location}")


def load_state(state: State):
    try:
        with open(f"{os.environ['HOME']}/.local/share/gitcoin_state.json", "r") as f:
            s = json.load(f)
            state.pubkey = s["pubkey"]
            state.privkey = s["privkey"]
            state.repo_location = s["repo_location"]
    except:
        pass


def write_state(state: State):
    with open(f"{os.environ['HOME']}/.local/share/gitcoin_state.json", "w") as f:
        json.dump({
            "pubkey": state.pubkey,
            "privkey": state.privkey,
            "repo_location": state.repo_location
        }, f)


if __name__ == "__main__":
    run()
