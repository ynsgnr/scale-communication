#!/bin/env python3
import argparse
import asyncio
import logging
from bleak import BleakClient, BleakScanner, BleakGATTCharacteristic



###
# class scaleComm:
#  - Implements the communication protocol for the "Crenot Gofit S2" scale
###
class CrenotGofitS2:

    address = None
    client  = None

    print_dev_info = False
    print_svc_info = False

    is_weight_stable = False
    wait_stable_timeout = 10
    weight           = 0 # in grams

    def __init__(self, print_dev_info=False, print_svc_info=False, timeout=10):
        self.print_dev_info = print_dev_info
        self.print_svc_info = print_svc_info
        self.wait_stable_timeout = timeout

    async def run(self):
        name = "Crenot Gofit S2"
        if not await self.connect(name):
            logging.error(f"Could not connect to scale '{name}'")
            return False
            
        logging.info(f"Connection to scale '{name}' established")

        if self.print_dev_info:
            await self.get_device_information()
        if self.print_svc_info:
            await self.print_services()
        
        await self.start_notification("FFB2", self.on_ffb2_notification)
        # await self.start_notification("FFB3", self.on_ffb3_notification)
        # await self.start_notification("2A05", self.on_2a05_notification)

        logging.info(f"Waiting for weight to stabilize (timeout:{self.wait_stable_timeout}s)" )

        try:
            async with asyncio.timeout(self.wait_stable_timeout):
                while not self.is_weight_stable:
                    logging.debug(f"weight:{self.weight}")
                    await asyncio.sleep(1)
                logging.info(f" - Weight: {self.weight/1000: .2f}kg")
        except asyncio.TimeoutError:
            logging.error(f" - Timeout (Last weight: {self.weight/1000: .2f}kg)")
        except asyncio.CancelledError:
            logging.error(f" - Cancelled (Last weight: {self.weight/1000: .2f}kg)")
        except Exception as e:    
            logging.error("Waiting for stable weight failed with exception", e)
            
    ###
    # connect()
    #  - discover ble devices
    #  - search for a device with the specified name
    #  - connect to it (if found)
    #    
    #
    # parameters:
    #  - name: name of the scale (e.g. "Crenot Gofit S2")
    #
    # return value:
    #  - True if a scale with the specified name was found and the connection could be established.
    #  - False if no matching device was found or if the connection could not be established.
    ###
    async def connect(self, name):

        logging.info("Discovering BLE devices")
        devices = await BleakScanner.discover()
        for d in devices:
            if d.name == name:
                self.address = d.address
                break
        if self.address == None:
            return False

        logging.info(f"Connecting to scale '{name}'")
        self.client = BleakClient(self.address)
        try:
            await self.client.connect()
            return True
        except Exception as e:
            logging.error("Connect failed with exception", e)
        return False

    ###
    # get_device_information()
    #  - read available device information fields and log its values
    ###
    async def get_device_information(self):

        logging.info("Gathering device information")
        device_info = { "system id"    : "2A23",
                        "model number" : "2A24",
                        "serial number": "2A25",
                        "fw revision"  : "2A26",
                        "hw revision"  : "2A27",
                        "sw revision"  : "2A28",
                        "manufacturer" : "2A29" }
                    
        for type, uuid in device_info.items():
            try:
                value = await self.client.read_gatt_char(uuid)
                logging.info( f" - {type: <16s}: {value.decode('utf-8', 'backslashreplace')}" )
            except Exception as e:
                pass
                logging.error( f" - {type: <16s}: failed" )

    ###
    # print_services()
    #  - gathers and prints information about available services and characteristics
    ###
    async def print_services(self):
        
        logging.info("Gathering service information")
        for s in self.client.services:
            logging.info(f" - {s.uuid: <36s}: {s.description}")

    ###
    # start_notification()
    #  - triggers the scale to send notification/indication messages for the given uuid
    ###
    async def start_notification(self, uuid, callback):
        
        logging.info(f"Starting notifications for uuid {uuid}")
        await self.client.start_notify(uuid, callback)

    ###
    # on_xxxx_notififaction()
    #  - called when notification/indication message of according uuid is received
    ###
    async def on_ffb2_notification(self, sender: BleakGATTCharacteristic, data: bytearray):
        logging.debug(f" - FFB2: received data {data.hex()}")
        if not self.is_weight_stable:
            # weight is stored in bytes 6, 7 and 8 but only 2 bits of byte 6 are used
            # therefore we extract the value by binary or operation 262143
            self.weight = int.from_bytes([ data[6], data[7], data[8] ]) & 262143
            if data[4] == 2:
                self.is_weight_stable = True

    async def on_ffb3_notification(self, sender: BleakGATTCharacteristic, data: bytearray):
        logging.info(f" - FFB3: received data {data.hex()}")

    async def on_2a05_notification(self, sender: BleakGATTCharacteristic, data: bytearray):
        logging.info(f" - 2A05: received data {data.hex()}")



# Execute when the not initialized from an import statement.
if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Client application for 'Crenot Gofit S2' scale")
    parser.add_argument('--print_dev_info', action='store_true', help='enable output of device information')
    parser.add_argument('--print_svc_info', action='store_true', help='enable output of service information')
    parser.add_argument('--timeout', type=float, default=10, help='timeout when waiting for weight to stabilize')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format=" - %(levelname)s \t%(message)s")
    asyncio.run(CrenotGofitS2(print_dev_info=args.print_dev_info,
                              print_svc_info=args.print_svc_info,
                              timeout=args.timeout).run())    
