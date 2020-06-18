"""
Scan/Discovery
--------------

Example showing how to scan for BLE devices.

Updated on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>

"""

import asyncio
from bleak import discover

from bleak import BleakClient
from bleak import _logger as logger
from bleak.uuids import uuid16_dict

import list_et

service_uuid = '7b183224-9168-443e-a927-7aeea07e8105'
count_uuid = '292bd3d2-14ff-45ed-9343-55d125edb721'
rw_uuid = '56cd7757-5f47-4dcd-a787-07d648956068'

async def get_counts(device):
    async with BleakClient(device.address) as client:
        # print(device.name, end=" ")
        x = await client.is_connected()
        # print("Connected: {0}".format(x))
        c = await client.read_gatt_char(rw_uuid)
        # print('last rw command: ',c)
        count = await client.read_gatt_char(count_uuid)
        count = int.from_bytes(bytes(count), byteorder='little')
        # print('count', count, int.from_bytes(bytes(count), byteorder='little'))
        return c, count
async def run():
    #devices = await discover()
    print("Trying to find NIST ET devices")
    et_devices = await list_et.get_et_list()

    # name = 'NIST0005'
    #
    # for device in et_devices:
    #     if device.name == name:
    #         not_found = False
    #         break
    # result = await get_counts(device)
    # print(device, result)
    for device in et_devices:
        print('*'*80)
        print(f"trying to fetch from {device.name}")
        while True:
            result = await get_counts(device)
        print(device.name, result)
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
