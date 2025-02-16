# Gitcoin
The furturistic and revolutionizing next-generation cryptocurrency built for developers, by developers.

## Installation
``` bash
pip install gitcoin
```

## Usage
First, set up your public and private key to officially mark your entrance into Gitcoin.
``` bash
gitcoin keypair gen
```

Next, you may start mining to obtain Gitcoins
``` bash
gitcoin mine
```

With Gitcoins now in your balance, you may initiate transactions with other users in the network.
Transactions are made to another user via their public key, followed by the desired amount. This (destination, amount) pair may continue indefinitely, ended with a custom amount of transaction fee (default is 1). 
After your transaction is validated by miners, incentivized by your generous (or not) fee, you are now officially part of the Gitcoin blockchain that will go down in history, forever and ever!
``` bash
gitcoin pay <public-key> <amount>
```

General Gitcoin assistance is done with:
```bash 
gitcoin --help
```
More specific help is done with:
```bash
gitcoin <option> --help
```

The possible options for Gitcoin is:
| Option | Function |
| ------ |  ------  |
| pay    | pays someone, duh|
| remote | retrieving Gitcoin blockchain |
| mine   | mines Gitcoin |
| observer | observes own blockchain |
| keypair | generates keypairs for user |
| repo | retrieves repo location |

## Features
Great animation soothing our soul as we transact and mine Gitcoins!

#
# Packages
* In case packages need fixing, to install all packages necessary: `pip install -r requirements.txt`

# Testing
* Running tests for transactions (from ./Gitcoin directory):
    * `pytest -k test_transaction_simple`
    * `pytest -k test_coinbase_transaction_simple`
    * `pytest -k test_transaction_already_used`
    * `pytest -k test_transaction_excess`
    * `pytest -k test_transaction_nightmare`

* Running tests for logic (from ./Gitcoin directory):
    * `pytest -k test_validate_tnx_simple`
    * `pytest -k test_tnxinfo_validate_signed`
    * `pytest -k test_tnxinfo_serialize_deserialize`
    * `pytest -k test_init_chain`

* Test to generate keys and sign a message, convert PEM strings back to key objects, and convert hex signature back to bytes and verify
    * `python test.py`

## Now featuring: HORSE
![black horse](res/black-horse-head.jpg)
![horse head](res/horse-head-portrait.jpg)
![white horse](res/horse-white.jpg)
