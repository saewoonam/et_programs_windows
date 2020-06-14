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
#global 
async def run():
    devices = await discover()
    addresses = []
    for d in devices:
        if d.metadata['uuids'] is not None:
            if service_uuid in d.metadata['uuids']:
                print(d.__dict__.keys())
                addresses.append(d.address)

    # async with BleakClient(address, loop=loop) as client:
    address = addresses[0]
    for address in addresses:
        print('*'*80)
        print('address', address)
        async with BleakClient(address) as client:
            x = await client.is_connected()
            logger.info("Connected: {0}".format(x))

            c = await client.read_gatt_char(rw_uuid)
            print('c: ',c)
            count = await client.read_gatt_char(count_uuid)
            print('count', count, int.from_bytes(bytes(count), byteorder='little'))
            
service_uuid = '7b183224-9168-443e-a927-7aeea07e8105'
count_uuid = '292bd3d2-14ff-45ed-9343-55d125edb721'
rw_uuid = '56cd7757-5f47-4dcd-a787-07d648956068'

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
