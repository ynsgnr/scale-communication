#!/bin/env python3
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

    is_weight_stable = False
    weight           = 0 # in grams

    async def run(self):
        name = "Crenot Gofit S2"
        if not await self.connect(name):
            logging.error(f"Could not connect to scale '{name}'")
            return False
            
        logging.info(f"Connection to scale '{name}' established")

        # await self.get_device_information()
        # await self.print_services()
        
        await self.start_notification("FFB2")
        # await self.start_notification("FFB3")
        # await self.start_notification("2A05")

        logging.info("Waiting for weight to stabilize")
        while not self.is_weight_stable:
            logging.debug(f"weight:{self.weight}")
            await self.get_device_information()
        
        logging.info(f" - Weight: {self.weight/1000: .2f}kg")
            
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

        # logging.info("Gathering device information")
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
                #logging.info(f" - {type: <16s}: '{value.decode("utf-8", "backslashreplace")}'")
            except Exception as e:
                pass
                #logging.error(f" - {type: <16s}: failed")

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
    async def start_notification(self, uuid):
        
        logging.info(f"Starting notifications for uuid {uuid}")
        await self.client.start_notify(uuid, self.notify_callback)

    ###
    # notify_callback()
    #  - called when notification/indication message is received
    ###
    async def notify_callback(self, sender: BleakGATTCharacteristic, data: bytearray):
        logging.debug(f" - received data {data.hex()}")
        if not self.is_weight_stable:
            self.weight = int.from_bytes([ data[6], data[7], data[8] ]) & 262143
            if data[4] == 2:
                self.is_weight_stable = True



# Execute when the not initialized from an import statement.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=" - %(levelname)s \t%(message)s")
    asyncio.run(CrenotGofitS2().run())    
