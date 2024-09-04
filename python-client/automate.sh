#!/bin/bash
# Usage: <timeout 600> automate.sh
# Start with Wi-Fi up and cellular down

cd /home/qifeid/Documents/cmu/openrtist/python-client
export PATH=$PATH:/home/qifeid/.local/bin
export DISPLAY=:1

# Randomly sleep for 0-1 minutes
sleep $(shuf -i 1-60 -n 1)
su -c "/home/qifeid/.local/bin/poetry run openrtist -c deluge.elijah.cs.cmu.edu:9099" qifeid
sleep 2
systemctl stop chrony.service
sleep 2
nmcli c down "CMU-SECURE"
sleep 2
nmcli c up "US Mobile"
# Randomly sleep for 0-1 minutes
sleep $(shuf -i 1-60 -n 1)
su -c "/home/qifeid/.local/bin/poetry run openrtist -c deluge.elijah.cs.cmu.edu:9099" qifeid
sleep 2
nmcli c down "US Mobile"
sleep 2
nmcli c up "CMU-SECURE"
sleep 2
systemctl restart chrony.service
