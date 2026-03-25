**HeadMouse: Assistive Cefalic Control Interface 🎯
Author: Héctor Vieira (21-00290) - Universidad Simón Bolívar (USB)**

Status: Alpha Prototype / Functional MVP

HeadMouse is a low-cost, open-source, wearable Human Interface Device (HID) designed to provide full computer cursor control and clicking capabilities to individuals with upper limb motor disabilities. It uses inertial tracking and Time-of-Flight (ToF) technology to translate head movements and neck tilts into high-precision mouse actions.


**⚙️ Hardware Architecture & Components**

The system is designed to be affordable (under $30 USD) and relies on the following minimal hardware:

Microcontroller: Arduino Nano (ATmega328P).

Inertial Sensor (IMU): MPU6050 (6-axis MEMS). Read directly via I2C registers to minimize overhead.

Click Sensor (ToF): Adafruit/Pololu VL53L0X. Emits an infrared laser to measure the distance to the user's shoulder.

Chassis: 3D Printed Clamshell design (Manufactured in a Bambu Lab using PLA/PBT hybrid filament for mechanical fatigue resistance).

Mounting: Woven elastic band routed through integrated chassis slots.


**🧠 Software Architecture**

The project is split into embedded firmware and a Python host driver:

C++ Firmware (Arduino): Implements a 1D Kalman Filter to mitigate gyroscopic drift and thermal noise. The ToF sensor handles click logic: <400ms (Left Click), 400-1000ms (Double Click), >1000ms (Right Click). Distances are set at 150mm (action threshold) and 170mm (release) to create a mechanical hysteresis band. A distance of <45mm acts as a physical clutch to pause tracking.

Python Driver (HeadMouseApp.py): An asynchronous, multithreaded GUI built with customtkinter. It auto-detects the Arduino on COM ports (Plug & Play) at 115200 baud. It implements a Dynamic Exponential Moving Average (EMA) filter. Mathematical friction adjusts dynamically based on vector velocity (α = 0.15 for slow precision aiming, α = 0.8 for fast screen crossing).

Machine Learning Colector (Entrenador_IA.py): An integrated mini-game that generates a "Ground Truth" Dataset (.csv). It collects real-time raw coordinates, smoothed coordinates, and click intent for future Long Short-Term Memory (LSTM) neural network training.


**🛠️ Assembly and Usage**

Hardware: Flash the .ino firmware to the Arduino Nano. Wire the MPU6050 and VL53L0X via I2C. Assemble the hardware inside the PLA/PBT clamshell casing and secure the elastic band.

Software Setup: * Install Python and ensure it is added to the system PATH.

Install dependencies: pip install pyserial pyautogui customtkinter keyboard.

Execution: Connect the USB. Run HEADMOUSE_DRIVER.PY for safety then HEADMOUSEAPP.py to launch the Master Hub GUI.

Calibration: Keep your head centered and press Ctrl+Shift+C. The system will capture 1500 samples to calculate the DC Offset.

Operation Modes: Select "Escritorio" for EMA filtered control, "Gaming" for 1:1 raw input, or "Entrenar IA" to launch the dataset collection environment.


**⚖️ License and Copyright**

The source code (Python and C++) is licensed under the Apache License 2.0. Copyright 2026 Héctor Vieira.

The hardware designs, 3D parametric models, and technical documentation are licensed under the Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). Created by Héctor Vieira.
