#!/usr/bin/env bash

echo "Setting up MoveMe... this might require admin privileges."

git clone git@github.com:chrisvoncsefalvay/moveme.git
sudo pip install -r requirements.txt

chmod ugo+x moveme.py
cp moveme.py /usr/bin/moveme

echo "Great, you can now execute MoveMe by typing moveme in the console."
