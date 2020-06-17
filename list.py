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

service_uuid = '7b183224-9168-443e-a927-7aeea07e8105'
count_uuid = '292bd3d2-14ff-45ed-9343-55d125edb721'
rw_uuid = '56cd7757-5f47-4dcd-a787-07d648956068'

async def get_et_list():
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
    return et_devices

async def run():
        devices = await get_et_list()
        print(len(devices))
        return devices
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    devices =  loop.run_until_complete(run())
    # devices =  asyncio.run(run())
    print(devices)
