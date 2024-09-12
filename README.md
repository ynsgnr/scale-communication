# scale-communication

This repository cotains my approach to reverse engineer and implement the protocol
for communication with a "Crenot Gofit S2" scale in Python by using Bleak.

Once the protocol is understood the scale also can be added to the [openScale](https://github.com/oliexdev/openScale) app.

## My scale

- Device name: [Crénot](https://crenot.com/) Gofit S2 (new model 2024)
- Manufacturer: ICOMON (from BLE scanner)
- Model number: FG2210LB (from BLE scanner)
- App: [Fitdays](https://play.google.com/store/apps/details?id=cn.fitdays.fitdays&hl=en_US)
- Chipset: [Chipsea](https://en.chipsea.com/product/dghly/) (based on Wireshark's name resolution of the devices physical address)

There also seem to be some identical scales with a different branding on the market (for example"Runstar FG2210").

### Pictures:
![scale](https://github.com/sroemer/scale-communication/blob/main/img/crenot_gofit_s2.jpg?raw=true)
![packaging](https://github.com/sroemer/scale-communication/blob/main/img/crenot_gofit_s2_box.jpg?raw=true)

## Versions / Changelog

- v0.2.0: Wait for weight to stabilize with a timeout and add command line arguments
- v0.1.1: Use asyncio.sleep() instead of dev. info requests to keep notifications incoming
- v0.1.0: The client is able to get the weight from the scale.

## Communication and data processing

1. Discover BLE devices
2. Connect to scale
3. Activate notifications/indications on characteristic 'FFB2'
4. Receive notifications for 'FFB2' and process data:
  - update weight value from bytes 6-8 (18 lowest bits)
  - if byte 4 is 2 stop updating the values (weight got stable) and exit
