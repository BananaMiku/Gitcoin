import argparse


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


parser = argparse.ArgumentParser()
parser.add_argument('-p', "--pay", nargs='+', help="Paying a desintination a certain amount of Gitcoin with fess",
                    type=dest_and_amt)

args = parser.parse_args()

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


