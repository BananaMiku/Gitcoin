import argparse
import subprocess
from gitcoin.transact import make_keys

# only integer transactions are allowed
def dest_and_amt(input):
    # try parsing argument for 'Pay' command
    # print(input)
    try: 
        args = input.split(' ')
    except Exception:
        print("Invalid Argument Sequences for 'Pay' comand.")
    
    for i in range(len(args)):
        # even index = destinations
        if i % 2 == 0 and type(args[i]) != str:
            raise TypeError("Destination must be a string.")
        if i % 2 != 0 and type(args[i]) != int:
            raise TypeError("Amount must be an integer.")
    
    return args


def run():
    parser = argparse.ArgumentParser()
    # subparser accepts only one option name (no short and long)
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # payment command
    parser.add_argument('-p', "--pay", nargs='+', help="Paying a desintination a certain amount of Gitcoin with fess",
                        type=dest_and_amt)

    # subparser for remote command
    remote_parser = subparsers.add_parser("remote", help="git remote clone")
    remote_subparsers = remote_parser.add_subparsers(dest="remote_action", help="sub-command help")

    # subparser remote add 
    remote_add_parser = remote_subparsers.add_parser( "add", help="git remote add clone")
    remote_add_parser.add_argument("name", help="Name of the remote", type=str)
    remote_add_parser.add_argument("url", help="URL of the remote", type=str)
    # subparser remote remove
    remote_remove_parser = remote_subparsers.add_parser( "remove", help="git remote remove clone")
    remote_remove_parser.add_argument("name", help="Name of the remote", type=str)

    keypair_parser = subparsers.add_parser("keypair", help="generate or set keypairs")
    keypair_subparsers = keypair_parser.add_subparsers(dest="keypair_action", help="idk")

    keypair_subparsers.add_parser("generate", help="generate private key")
    keypair_set_parser = keypair_subparsers.add_parser("set", help="set your private key")
    keypair_set_parser.add_argument("privkey", help="your private key", type=str)

    # mine command
    parser.add_argument("-m", "--mine", help="Mine Gitcoin, with love <3", action="store_true") 

    # observer command
    parser.add_argument("-o", "--observer", help="TAKE A LOOK AT YOUR OWN BLOCKCHAIN", action="store_true")

    args = parser.parse_args()

    # not subcommand
    if args.pay:
        # try python main.py --pay A 1 B 2 C 33 40
        payment_info = args.pay
        # if args.pay is odd, the last element is the fee, default fee otherwise
        if len(payment_info) % 2 != 0:
            fee = args.pay.pop(-1)
        else:
            fee = 1

        print(f"fee is {fee}")
        for i in range(0, len(payment_info), 2): # should be even in length
            print(f"Destination: {payment_info[i]}, Amount: {payment_info[i+1]}")

    # subcommand
    if args.command == "remote":
        print('remote')
        if args.remote_action == "add":
            print(f"Adding remote: {args.name} with URL: {args.url}")
            subprocess.Popen(f'git remote add {args.name} {args.url}', shell=True)
        elif args.remote_action == "remove":
            print(f"Removing remote: {args.name}")
            subprocess.Popen(f'git remote rm {args.name}', shell=True)

        else:
            raise Exception("Invalid remote command")

    if args.command == "keypair":
        if args.keypair_action == "set":
            print(f"setting private key {args.privkey}")
        if args.keypair_action == "generate":
            [priv, pub] = make_keys()
            print(f"keys:\nprivate {priv}\npublic: {pub}\n\nthese are saved")
    
    # mine command going thru
    if args.mine:
        print("Mining Gitcoin...")

    # observer command going thru
    if args.observer:
        print("Observer placeholder")
