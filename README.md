# A small demo app for the python-xbee library

We used this script as a starting point for an XBee/ZigBee project
when we were trying to figure out how to get an Arduino and a
RaspberryPi talking to each other over ZigBee (Xbee chips).

## What does it do?

The script implements basic ping-pong messaging. The hub (RaspberryPi)
waits for a message, prints the message to stdout, and replies with a
"PONG" message.

The edge node sends an initial "PING" message after which it prints
out any received messages and replies to the sender with another
"PING" message.

We ran the script in hub mode on a Raspberry Pi and in edge node mode
on a laptop (the XBee chip was connected to the laptop over a USB
cable and one of these).

## How do I run the scripts?

The hub:

```shell
export XBEE_PORT=/dev/ttyAMA0
export IS_HUB=True
python xbee-demo.py
```

The edge node (laptop):

```shell
export XBEE_PORT=/dev/tty.usbserial-A1011HQ7
python xbee-demo.py
```

The hub out put should look something like this:

```shell
$ python xbee-demo/xbee-demo.py
run...

current status:

AT - ID = 00000000deadbeef
AT - SH = 0013a200
AT - SL = 40acc066
AT - MY = 0000

hub node - waiting for data
RX - {'source_addr_long': '\x00\x13\xa2\x00@\xb4\x175', 'rf_data': '\x03\xae', 'source_addr': 'k\x08', 'id': 'rx', 'options': '\x01'}
tx_status - {'retries': '\x00', 'frame_id': '\x01', 'deliver_status': '\x00', 'dest_addr': 'k\x08', 'discover_status': '\x00', 'id': 'tx_status'}
RX - {'source_addr_long': '\x00\x13\xa2\x00@\xb4\x175', 'rf_data': '\x03\x96', 'source_addr': 'k\x08', 'id': 'rx', 'options': '\x01'}
...
```

The edge node output should look something like this:

```shell
% python xbee-demo/xbee-demo.py
run...

current status:

AT - ID = 00000000deadbeef
AT - SH = 0013a200
AT - SL = 40b41735
AT - MY = 6b08

edge node - send frame to
tx_status - {'retries': '\x00', 'frame_id': '\x01', 'deliver_status': '\x00', 'dest_addr': '\x00\x00', 'discover_status': '\x00', 'id': 'tx_status'}
RX - {'source_addr_long': '\x00\x13\xa2\x00@\xac\xc0f', 'rf_data': 'PONG', 'source_addr': '\x00\x00', 'id': 'rx', 'options': '\x01'}
...
```

As you can see, the edge node initiates the messaging by sending the
first message (the edge node log starts with a `tx_status`).

## How to configure the XBee chips?

I won't go into a lot of detail on how to configure the
chips. Basically we used X-CTU on a Mac to flash the Coordinator API
firmware on the hub node chip and the End Device API firmware on the
edge node chip.

We then set the PAN ID to `0xDEADBEEF` in our case (come up with your
own PAN ID for you project ;-).

## Addressing

One of the key discoveries for us was to work out how to address the
hub node. In our use case the edge nodes will initiate comms with a
request to the hub and the hub will reply to the edge nodes.

The python-xbee `ZigBee.tx` calls require both a long destination
address (`dest_long_addr`) and a short destination address
(`dest_addr`). To address the hub (ie a Coordinator node) we can use a
long destination address of all `0`s and a destination address of
`0xFFFE` (unknown / breadcast address). These addresses allowed us to
send a message successfully from the edge node to the hub.

The hub can pick up the sender addresses from the packet and use those
when replying to the edge node.

## Requirements

This demo works with the
[python-xbee](https://github.com/markfickett/python-xbee) library.

## XBee vs. ZigBee

The `python-xbee` library provides both an `XBee` class and a `ZigBee`
class. Turns out that the `ZigBee` class implements the ZigBee
protocol, whereas the `XBee` class implements the lower level IEEE
802.15.4 protocol.

Our example script uses `ZigBee` rather than `XBee`.
