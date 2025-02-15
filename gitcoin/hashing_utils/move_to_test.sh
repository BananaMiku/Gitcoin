#!/bin/bash

TEST_REPO=/home/maxwell/Repositories/git-test/repo_a

. ../../.venv/bin/activate
pip install -e ../..

cp mine_cpu.abi3.so $TEST_REPO
cp mine_block.py $TEST_REPO

