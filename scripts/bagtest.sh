#!/bin/bash

# bagtest.sh - cleans up a directory being
# used for testing bags.  Just a quick 
# way to run a couple commands

sudo chown -R mjg36 /tmp/testbag
sudo chmod -R g+w /tmp/testbag
rm -f /tmp/testbag/*.txt 
mv /tmp/testbag/data/* /tmp/testbag/
rmdir /tmp/testbag/data
