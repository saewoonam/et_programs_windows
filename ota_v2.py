import asyncio
from bleak import discover

from bleak import BleakClient
from bleak import _logger as logger
from bleak.uuids import uuid16_dict

from consolemenu import *
from consolemenu.items import *

import list
import datetime
import time

service_uuid = '7b183224-9168-443e-a927-7aeea07e8105'
count_uuid = '292bd3d2-14ff-45ed-9343-55d125edb721'
rw_uuid = '56cd7757-5f47-4dcd-a787-07d648956068'
data_uuid = 'fec26ec4-6d71-4442-9f81-55bc21d658d6'


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

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(packet_index=0, total=0, not_done=True, packet_size=0)
def data_handler(sender, data):
    if data_handler.total==0:
        # set packet_size with the first packet
        data_handler.packet_size = len(data)
    #  Check if data came over correctly
    #  check packet number, check size
    print("data_handler")
    packet_index_received = int.from_bytes(data[:4], byteorder=='little')
    if (total_expected-total)>= (data_handler.packet_size-4):
        expected_len = data_handler.packet_size
    else:
        expected_len = total_expected-total + 4

    if (handler.packet_index == packet_index_received) and (len(data) == expected_len):
        data_handler.total += len(data) - 4
        print(f'\ridx: {packet_index_received} packet_len:{len(data)} received:{data_handler.total} / {num_records*32}', end='')

        if packet_len>0:
            fp_out.write(data[4:])

        # check if done
        if total_len == (num_records<<5):
            print("\nDone with xfer")
            # fp_out.close()
            data_handler.not_done = False
        else:
            # not done, request next packet
            data_handler.packet_index += 1
            get_idx = data_handler.packet_index
            # print('send get_idx: ', get_idx, get_idx.to_bytes(4, byteorder='little'))
            data_service.write_value(get_idx.to_bytes(4, byteorder='little'))
    else:
        get_idx = data_handler.packet_index
        print("ask for packet {get_idx} again\r\n")
        data_service.write_value(get_idx.to_bytes(4, byteorder='little'))


async def run():
    #devices = await discover()
    not_found = True
    while not_found:
        print("Trying to find NIST ET devices")
        et_devices = await list.get_et_list()
        print(et_devices)

        name = 'NIST0005'

        for device in et_devices:
            if device.name == name:
                not_found = False
                break
   
    print(device.name, device.address)
    c, num_records = await get_counts(device)
    print(num_records)
    # calculate number of 240 byte packets that need to be sent
    num_chunks = num_records*32 / 240
    if (num_records*32)%240 == 0:
        num_chunks -= 1
    print("num_32byte_records, num bytes, num_chunks to fetch: ", num_records, num_records*32,
          num_chunks)
    total_len = 0
    done_xfer = False
    if num_records==0:
        done_xfer = True
    else:
        date_suffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # fp_out = open('raw_'+date_suffix+'.bin', 'wb')
    print('*'*40)
    start=time.time()
    async with BleakClient(device.address) as client:
        x = await client.is_connected()
        logger.info("Connected: {0}".format(x))

        await client.start_notify(data_uuid, data_handler)
        await client.write_gatt_char(rw_uuid, bytearray(b'f'))
        while data_handler.not_done:
            await asyncio.sleep(1.0, loop=loop)
        await client.stop_notify(data_uuid)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
