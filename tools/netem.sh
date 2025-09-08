#!/usr/bin/env bash
sudo tc qdisc add dev eth0 root netem delay 120ms loss 1%
# remove: sudo tc qdisc del dev eth0 root
