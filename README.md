# Filament_Dryer
This Repo contains code and circuit for a DIY filament dryerthat heats up to a selected temperature, keeps the humidity at most at the target humidity for the selected duration. You need to print the casing of it youself as of now. The code is written for micropython. The maximum temperature, if your filament used for the casing, heater and fan allow it is 125°C which is the limit of what the DHT22 sensor can handle. The code currently only allows 90°C but it can be easily changed.

## BOM  
  - BC337 x2 npn-transistor
  - 5v Relais module that switches on if in is pulled low
  - button
  - ky-040 rotary encoder
  - ssd1306 lcd
  - dht22 sensor
  - small fan
  - 220V AC heater
  - 1kOhm resistor x2
  - RP2040 zero
  - 5v power supply
  - thermal fuse (optional)
  - electric fuse (optional)

## The Setup Explanation
The heater, fan and sensor are placed inside the filament dryer (to be 3d printed). The fan pulls air from outside to reduce humidity, the heater heats up the air to increase temperature. The sensor measures both humidity and temperature.
The button is ment as a start/stop button starting heating and stopping heating process. The rotary encoder allows one to set target humidity, duration and target temperature for the drying process. Here the rotary encoder button is used to cycle between the settings. I absolutely recommend using a thermal fuse inside the filament dryer for safety if something fails and the heater remains on for some reason. Also i would always add an appropriately sized electrical fuse inline with main input.

### Heater power
I used an old hairdryer and stripped it down to the heater, then removed the thermal fuse inside. However one can easily get cheap ptc heater from china. I would go with one that has an integrated fan. 100W should surely suffice for a dryer that can hold 2 rolls (probably 50W would be okay too) and has walls of at least 1cm with low infill for insulation. 

## How to use
First you need to design your casing. I will add mine soon, then you also have the option to use it as is. You should adapt the maximum temperature that is selectable based on the filament you used and what fan and heater tollerate. Generally abs fans might fail early due to temperature at 80 degrees. The current code allows 90 degrees which was safe for the abs filament i used to print the dryer. 

After the circuit is in place install micropython on you device. Then copy the files from inside `Font`, `SSD1306_Custom_Font.py`, `button.py` and `main.py` to the root of you device.

## Final notes
I might add my .stl files soon once i cleaned them up from the prototyping i did.

## breadboard for testing
I should not need to say this but don't connect anything to main AC when testing.
<img width="3636" height="2551" alt="Filament dryer_Steckplatine" src="https://github.com/user-attachments/assets/c25cc1e8-6b11-4f67-acb5-f70e3bcee56c" />

## circuit
![Filament dryer_Schaltplan](https://github.com/user-attachments/assets/89f700a1-8644-4394-b183-0b65918ae4cb)
