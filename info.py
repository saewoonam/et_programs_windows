"""
List info about ET devices
--------------

Copyright 2020  Sae Woo Nam
"""

import asyncio
from bleak import discover
from bleak import BleakClient
import sys

service_uuid = '7b183224-9168-443e-a927-7aeea07e8105'
count_uuid = '292bd3d2-14ff-45ed-9343-55d125edb721'
rw_uuid = '56cd7757-5f47-4dcd-a787-07d648956068'
data_uuid = 'fec26ec4-6d71-4442-9f81-55bc21d658d6'

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

g_xfer_done = False
def data_handler(sender, data):
    global g_data, g_xfer_done
    # print("sender, data", sender, data)
    g_data = data
    g_xfer_done = True

async def get_client(device):
    if True:
        client = BleakClient(device.address)
        connected = False
        print(f"Try to connect to {device.name}: {device.address}")
        while not connected:
            try: 
                connected = await client.connect()
            except Exception as e:
                print(e)
                print("Waiting")
                await asyncio.sleep(3)
                print("trying again")
    return client

async def put_rw(client, b):
    await client.write_gatt_char(rw_uuid, bytearray(b))

async def get_rw(client):
    return await client.read_gatt_char(rw_uuid)

async def get_info(client):
    global g_xfer_done, g_data
    # print(device.name, end=" ")
    x = await client.is_connected()
    # print("Connected: {0}".format(x))
    c = await get_rw(client)
    # print('last rw command: ',c)
    count = await client.read_gatt_char(count_uuid)
    count = int.from_bytes(bytes(count), byteorder='little')
    # print('count', count)

    await client.start_notify(data_uuid, data_handler) # , kw)
    # print("Started notify")
    # await client.write_gatt_char(rw_uuid, b'I')
    await put_rw(client, b'I')
    # print("sent I")
    g_xfer_done = False
    while not g_xfer_done:
        await asyncio.sleep(0.01)
    return c, count, g_data

async def run(dev_num=5, num=4, command=None):
    et_devices = await get_et_list(num)
    name = "NIST%04d"%dev_num

    for device in et_devices:
        if device.name == name:
            not_found = False
            break
    if not_found:
        print("can't find the device, exiting")
        sys.exit(1)
    client = await get_client(device)
    if command is not None:
        await put_rw(client, command)

    results = await get_info(client)
    if results[2]==b'\x00':
        write_status = "OFF"
    elif results[2]==b'\x01':
        write_status = "ON"
    else:
        write_status = "??"
  
    print(f"{device.name}: last_rw: {results[0]}, counts: {results[1]}, write_status: {write_status}")
    await client.disconnect()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Not enough arguments")
        sys.exit(1)
    elif len(sys.argv) >= 3:
        device_number = int(sys.argv[1])
        number_to_find = int(sys.argv[2])
    elif len(sys.argv) == 2:
        device_number = int(sys.argv[1])
        number_to_find = 4
    global loop
    loop = asyncio.get_event_loop()
    print("looking for NIST ET bluetooth devices")
    devices = loop.run_until_complete(run(device_number, number_to_find))
    # devices =  asyncio.run(run())
    # print(devices)
