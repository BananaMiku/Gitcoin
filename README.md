# GitCoin
2025 HackHer
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

# Now featuring: HORSE
![black horse](res/black-horse-head.jpg)
![horse head](res/horse-head-portrait.jpg)
![white horse](res/horse-white.jpg)
