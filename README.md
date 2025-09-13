# Filament Dryer

This repository contains code and circuit diagrams for a DIY filament dryer.  
It can heat up to a selected temperature and maintain humidity below a set target for a chosen duration.  

- The casing must currently be 3D printed by yourself.  
- The code is written in **MicroPython**.  
- The DHT22 sensor limits operation to a maximum of **125 °C**.  
- The provided code restricts temperature to **90 °C** by default (safe for most ABS-printed casings), but this can be adjusted if your heater, fan, and enclosure material allow it.  
<img src="https://github.com/user-attachments/assets/ffa3544b-6fdd-4d37-8279-b73a07e6f216" alt="WhatsApp Image" width="500"/>

---

## Bill of Materials (BOM)  

| Component             | Notes |
|-----------------------|-------|
| BC337 ×2              | NPN transistors |
| 5 V relay module      | Active low (switches when input pulled low) |
| Push button           | Start/stop heater |
| KY-040 rotary encoder | With push function to switch settings |
| SSD1306 LCD           | Display |
| DHT22 sensor          | Measures humidity & temperature (max 125 °C) |
| Small fan             | Circulates and exchanges air |
| 220 V AC heater       | Heating element (e.g. stripped hairdryer or PTC module) |
| 1 kΩ resistors ×2     | General purpose |
| RP2040 Zero           | Microcontroller running MicroPython |
| 5 V power supply      | To power control electronics |
| Thermal fuse (recommended)  | Safety cutoff |
| Electrical fuse (recommended) | Mains protection |

---

## Setup Explanation  

- **Inside the dryer**: heater, fan, and sensor are installed.  
- **Operation**:  
  - The **fan** pulls in outside air to reduce humidity.  
  - The **heater** warms the air to increase temperature.  
  - The **sensor** monitors both humidity and temperature.  
- **Controls**:  
  - The **button** acts as a start/stop switch.  
  - The **rotary encoder** sets target humidity, temperature, and drying duration.  
  - The encoder’s push button cycles between settings.  

Strongly recommended:  
- Install a **thermal fuse** in series with the heater.  
- Install an **electrical fuse** inline with the AC input.  

---

### Heater Power Notes  

- What i did: repurposed heater coil from an old hairdryer (thermal fuse removed).  
- Alternative: **PTC heaters with integrated fans** are inexpensive and safer.  
- Suggested power:  
  - **50–100 W** is usually enough for a 2-roll dryer with ≥1 cm thick insulated walls.  
  - Higher power is unnecessary and can be unsafe.
  - You can insulate the heater further with packaging foam from the outside to increase efficiency, then the heater can be downscaled further.

---

## How to Use  

1. **Design or print your casing.**  
   - STL files will be added here once cleaned up from prototyping.  
   - Adjust the maximum selectable temperature to match your filament, fan, and heater tolerances.  
   - Note: ABS fans may degrade at ~80 °C (3D printing filaments often handle more temp). Be sure to use non ABS fans or if you have a fan already you can test if it is ABS by putting aceton onto parts of it. If it melts its most likely ABS.  

2. **Install MicroPython** on the RP2040 Zero.  

3. **Copy the following files** to the device root:  
   - `Font/*`  
   - `SSD1306_Custom_Font.py`  
   - `button.py`  
   - `main.py`
    Note that you need to copy the files inside the `Font` folder not the folder itself.

4. **Assemble the circuit** according to the diagrams below.  

---

## Breadboard for Testing  

⚠️ Do **not** connect anything to mains AC when testing on breadboard.  

<img width="3636" height="2551" alt="Filament dryer breadboard" src="https://github.com/user-attachments/assets/c25cc1e8-6b11-4f67-acb5-f70e3bcee56c" />

---

## Circuit Diagram  

![Filament dryer circuit](https://github.com/user-attachments/assets/89f700a1-8644-4394-b183-0b65918ae4cb)

---

## ⚠️ Disclaimer  

This project involves **mains electricity** and **heating elements**, which can be dangerous.  
It is provided *as-is*, **without warranty of any kind**.  
You build and use it **at your own risk**.  

Always include:  
- A properly rated **thermal fuse** inside the dryer.  
- An appropriate **electrical fuse** inline with the AC input.  
- Careful consideration of enclosure material (temperature tolerance, fire safety).  

---

## License  

This project is licensed under the **MIT License** – see the [LICENSE](./LICENSE) file for details.  
