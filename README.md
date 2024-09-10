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

## Status

Currently the code only discovers available BLE devices and connects to a device
with the name "Crenot Gofit S2" (if available).
