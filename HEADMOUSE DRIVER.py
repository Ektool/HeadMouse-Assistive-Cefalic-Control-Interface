# Copyright 2026 Héctor Vieira 
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import serial
import serial.tools.list_ports
import pyautogui
import time
import sys

BAUD_RATE = 115200
# --- SOLUCIÓN MULTI-MONITOR ---
pyautogui.PAUSE = 0.0 
pyautogui.FAILSAFE = False # ¡ESTO EVITA QUE SE CONGELE AL TOCAR BORDES!

def buscar_headmouse_rapido():
    print("Buscando el HeadMouse...")
    puertos = [p for p in serial.tools.list_ports.comports() if "Bluetooth" not in p.description]
    if not puertos: return None
    for puerto in puertos:
        try:
            prueba = serial.Serial(puerto.device, BAUD_RATE, timeout=0.5)
            time.sleep(1) 
            for _ in range(4):
                linea = prueba.readline().decode('utf-8', errors='ignore').strip()
                if "CALIBRANDO" in linea or "EXITOSA" in linea:
                    prueba.close()
                    return puerto.device
            prueba.close()
        except Exception: pass
    return None

PUERTO_DETECTADO = buscar_headmouse_rapido()

if not PUERTO_DETECTADO:
    print("\n[!] No se detectó el HeadMouse. Cierra el Monitor Serie de Arduino IDE.")
    sys.exit()

try:
    print(f"Iniciando en {PUERTO_DETECTADO}... ¡MANTÉN LA CAJA QUIETA 3 SEGUNDOS!")
    arduino = serial.Serial(PUERTO_DETECTADO, BAUD_RATE, timeout=0.1)
    time.sleep(3.5) 
    arduino.flushInput()
    print("¡Listo! (Puedes minimizar esta ventana).")

    while True:
        if arduino.in_waiting > 0:
            linea = arduino.readline().decode('utf-8', errors='ignore').strip()
            if not linea or "CALIB" in linea or "EXITOSA" in linea: continue
                
            try:
                datos = linea.split(',')
                if len(datos) == 3:
                    moveX = int(datos[0])
                    moveY = int(datos[1])
                    comando_clic = int(datos[2])
                    
                    if moveX != 0 or moveY != 0:
                        pyautogui.moveRel(moveX, moveY)
                    
                    # --- NUEVA LÓGICA DE CLICS ---
                    if comando_clic == 1:
                        pyautogui.click(button='left')
                        print("-> Clic Izquierdo")
                    elif comando_clic == 2:
                        pyautogui.click(button='right')
                        print("-> Clic Derecho")
                    elif comando_clic == 3:
                        pyautogui.doubleClick()
                        print("-> DOBLE CLIC")
                        
            except ValueError: pass

except Exception as e:
    print(f"Error: {e}")