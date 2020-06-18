"""
List info about ET devices
--------------

Copyright 2020  Sae Woo Nam
"""

import asyncio
from bleak import discover
from bleak import BleakClient
import sys

from consolemenu import *
from consolemenu.items import *

service_uuid = '7b183224-9168-443e-a927-7aeea07e8105'
count_uuid = '292bd3d2-14ff-45ed-9343-55d125edb721'
rw_uuid = '56cd7757-5f47-4dcd-a787-07d648956068'

async def get_et_list(num=4):
    found = False
    while not found:
        devices = await discover()
        et_devices = []
        for d in devices:
            # print(d.__dict__.keys())
            # print(d.address)
            # print(d.details)
            if 'uuids' in d.metadata:
                # print(d.metadata['uuids'])
                if service_uuid in d.metadata['uuids']:
                    print(d.name)
                    et_devices.append(d)
        if len(et_devices)>= num:
            found = True
        else:
            print(f"Found {len(et_devices)}/{num}")
    return et_devices

async def get_counts(device):
    if True:
        client = BleakClient(device.address)
        connected = False
        print(f"Try to connect to {device.name}: {device.address}")
        while not connected:
            try: 
                connected = await client.connect()
            except Exception as e:
                print(e)
                print("Wait")
                await asyncio.sleep(3)
                print("try again")

        # print(device.name, end=" ")
        x = await client.is_connected()
        # print("Connected: {0}".format(x))
        c = await client.read_gatt_char(rw_uuid)
        print('last rw command: ',c)
        count = await client.read_gatt_char(count_uuid)
        count = int.from_bytes(bytes(count), byteorder='little')
        print('count', count, int.from_bytes(bytes(count), byteorder='little'))
        return c, count

async def run(num=4):
    devices = await get_et_list(num)
    print(len(devices))
    for dev in devices:
        print(await get_counts(dev))

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        number_to_find = int(sys.argv[1])
    else:
        number_to_find = 4
    global loop
    loop = asyncio.get_event_loop()
    print("looking for NIST ET bluetooth devices")
    devices = loop.run_until_complete(run(number_to_find))
    print(loop.is_closed())
    # devices =  asyncio.run(run())
    # print(devices)
