#!/bin/env python3
import asyncio
import logging
from bleak import BleakClient, BleakScanner



###
# class scaleComm:
#  - Implements the communication protocol for the "Crenot Gofit S2" scale
###
class CrenotGofitS2:

    address = None
    client = None

    async def run(self):
        name = "Crenot Gofit S2"
        if not await self.connect(name):
            logging.error(f"Could not connect to scale '{name}'")
            return False
            
        logging.info(f"Connection to scale '{name}' established")
        await self.get_device_information()
        await self.print_services()

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
                logging.info(f" - {type: <16s}: '{value.decode("utf-8", "backslashreplace")}'")
            except Exception as e:
                logging.error(f" - {type: <16s}: failed")

    ###
    # print_services()
    #  - gathers and prints information about available services and characteristics
    ###
    async def print_services(self):
        
        logging.info("Gathering service information")
        for s in self.client.services:
            logging.info(f" - {s.uuid: <36s}: {s.description}")





# Execute when the not initialized from an import statement.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=" - %(levelname)s \t%(message)s")
    asyncio.run(CrenotGofitS2().run())
