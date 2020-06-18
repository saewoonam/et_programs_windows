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

async def run(num=4):
    devices = await get_et_list(num)
    print(len(devices))
    return devices

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

def item_func(peripheral, override=None):
    global loop
    global total_len, done_xfer, data_service, out
    total_len = 0

    # loop = asyncio.get_event_loop()
    read_val, count_raw = loop.run_until_complete(get_counts(peripheral))
    if False:
        done_xfer = False
        out = b''
        def received(data):
            global total_len, done_xfer, data_service, out
            out += data
            packet_len = len(data)
            total_len += packet_len
            # print(total_len, out.hex(), data.hex())
            # print('Received {0} bytes total {1}'.format(packet_len, total_len))
            if total_len >= 1:
                # print("Done with xfer")
                data_service.stop_notify()
                done_xfer = True

        # Turn on notification of RX characteristics using the callback above.
        data_service.start_notify(received)
        # print("Send command to fetch info/status")
        rw.write_value(b'I')
        # print('rw.read_value()', rw.read_value())
        while not done_xfer:
            # print('waiting')
            time.sleep(0.1)
        print(type(out))
        print(out)
        if out == b'\x00':
            write = f": OFF"
        elif out == b'\x01':
            write = f": ON"
        else:
            write =f": {out.hex()}"

    # write = "XX"
    # selected = menu.selected_option
    # if override is not None:
    #     menu.items[override].text = f"{peripheral.name}: rw:{read_val} count:{count_raw} write:{write}"
    # else:
    #     menu.items[selected].text = f"{peripheral.name}: rw:{read_val} count:{count_raw} write:{write}"
    # # print(menu.__dict__)
    # menu.epilogue_text = "Last result: " + menu.items[selected].text
    # # input("Press Enter to continue.")

def all_item_func(devices):
    for idx, k in enumerate(devices.keys()):
        peripheral = devices[k]
        item_func(peripheral, override=idx)

def m(devices):
    # Create the root menu
    global menu
    menu = ConsoleMenu("Bluetooth Gadget get info", "")
    # Create a menu item that calls a function
    # for peripheral in devices:
    for peripheral in devices:
        item_name = peripheral.name + ": "+ peripheral.address
        function_item = FunctionItem(item_name, item_func, [peripheral])
        menu.append_item(function_item)

    function_item = FunctionItem('All', all_item_func, [devices])
    menu.append_item(function_item)

    menu.start()
    menu.join()


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        number_to_find = int(sys.argv[1])
    else:
        number_to_find = 4
    global loop
    loop = asyncio.get_event_loop()
    print("looking for NIST ET bluetooth devices")
    devices = loop.run_until_complete(run(number_to_find))
    # devices =  asyncio.run(run())
    # print(devices)
    # item_func(devices[0])
    m(devices)
