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

import tkinter as tk
from tkinter import messagebox
import serial
import serial.tools.list_ports
import time
import csv
import random
import math
import os
import sys

BAUD_RATE = 115200

class RecolectorIA:
    def __init__(self, root):
        self.root = root
        self.root.title("HeadMouse - Centro de Entrenamiento IA")
        self.root.geometry("800x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#111111")

        # --- AUTO-FOCO: Fuerza la ventana a saltar al frente ---
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.focus_force()

        # --- VARIABLES DEL JUEGO ---
        self.cursor_x = 400
        self.cursor_y = 300
        self.objetivo_x = 0
        self.objetivo_y = 0
        self.tipo_objetivo = 1
        self.ultimo_moveX = 0.0
        self.ultimo_moveY = 0.0
        self.arduino = None
        self.jugando = False

        # --- RUTA ABSOLUTA Y PROTECCIÓN DE ARCHIVO ---
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        self.archivo_db = os.path.join(directorio_actual, "base_datos_headmouse.csv")

        try:
            self.preparar_base_datos()
        except PermissionError:
            messagebox.showerror(
                "Error Crítico de Archivo", 
                "¡Cierra Excel o el Bloc de Notas!\n\n"
                f"Windows bloqueó el acceso a '{self.archivo_db}'."
            )
            self.root.destroy()
            sys.exit()

        self.crear_interfaz()
        self.conectar_arduino()

    def preparar_base_datos(self):
        if not os.path.exists(self.archivo_db):
            with open(self.archivo_db, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["crudoX", "crudoY", "cursorX", "cursorY", "objetivoX", "objetivoY", "tipo_objetivo", "clic_real"])

    def crear_interfaz(self):
        self.lbl_estado = tk.Label(self.root, text="Buscando HeadMouse...", font=("Arial", 16, "bold"), bg="#111111", fg="#F1C40F")
        self.lbl_estado.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=800, height=500, bg="#222222", highlightthickness=2, highlightbackground="#3498DB")
        self.canvas.pack()

        self.btn_iniciar = tk.Button(self.root, text="INICIAR ENTRENAMIENTO", font=("Arial", 14, "bold"), bg="#2ECC71", fg="white", command=self.iniciar_juego, state=tk.DISABLED)
        self.btn_iniciar.pack(pady=20)

    def conectar_arduino(self):
        puertos = [p for p in serial.tools.list_ports.comports() if "Bluetooth" not in p.description]
        puerto_detectado = None
        
        for puerto in puertos:
            try:
                prueba = serial.Serial(puerto.device, BAUD_RATE, timeout=0.5)
                time.sleep(1)
                for _ in range(3):
                    linea = prueba.readline().decode('utf-8', errors='ignore').strip()
                    if "CALIBRANDO" in linea or "EXITOSA" in linea:
                        puerto_detectado = puerto.device
                        break
                prueba.close()
            except: pass
            if puerto_detectado: break

        if puerto_detectado:
            self.lbl_estado.config(text=f"HeadMouse Conectado ({puerto_detectado}) - Listo para Entrenar", fg="#2ECC71")
            self.arduino = serial.Serial(puerto_detectado, BAUD_RATE, timeout=0)
            self.btn_iniciar.config(state=tk.NORMAL)
            self.root.after(10, self.bucle_principal)
        else:
            self.lbl_estado.config(text="Error: HeadMouse no encontrado. Revisa el USB.", fg="#E74C3C")

    def iniciar_juego(self):
        self.jugando = True
        self.btn_iniciar.config(state=tk.DISABLED, text="ENTRENANDO... (Usa el botón rojo para salir)", bg="#E74C3C")
        self.cursor_x = 400
        self.cursor_y = 300
        self.generar_objetivo()

    def generar_objetivo(self):
        self.objetivo_x = random.randint(100, 700)
        self.objetivo_y = random.randint(100, 400)
        self.tipo_objetivo = random.choice([1, 2, 3]) 
        self.dibujar_escena()

    def dibujar_escena(self):
        self.canvas.delete("all")
        if not self.jugando: return

        colores = {1: "#E74C3C", 2: "#3498DB", 3: "#2ECC71"} 
        textos = {1: "Clic\nNormal", 2: "Clic\nDerecho", 3: "Doble\nClic"}
        
        # Dibujar Objetivo
        color = colores[self.tipo_objetivo]
        self.canvas.create_oval(self.objetivo_x - 40, self.objetivo_y - 40, self.objetivo_x + 40, self.objetivo_y + 40, fill=color, outline="white", width=3)
        self.canvas.create_text(self.objetivo_x, self.objetivo_y, text=textos[self.tipo_objetivo], fill="white", font=("Arial", 11, "bold"), justify=tk.CENTER)

        # BOTÓN DE SALIDA VIRTUAL
        self.canvas.create_rectangle(680, 10, 790, 50, fill="#C0392B", outline="white", width=2)
        self.canvas.create_text(735, 30, text="SALIR (Clic)", fill="white", font=("Arial", 10, "bold"))

        # Cursor
        self.canvas.create_oval(self.cursor_x - 12, self.cursor_y - 12, self.cursor_x + 12, self.cursor_y + 12, fill="#F1C40F")

    def bucle_principal(self):
        if self.arduino and self.arduino.in_waiting > 0:
            try:
                linea = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                if linea and "CALIB" not in linea and "EXITOSA" not in linea:
                    datos = linea.split(',')
                    if len(datos) == 3:
                        crudoX = float(datos[0])
                        crudoY = float(datos[1])
                        comando_clic = int(datos[2])

                        if crudoX == 0 and crudoY == 0:
                            self.ultimo_moveX, self.ultimo_moveY = 0, 0
                            moveX, moveY = 0, 0
                        else:
                            vel = (abs(crudoX) + abs(crudoY))
                            alpha = 0.15 if vel < 15 else 0.8
                            moveX_f = (alpha * crudoX) + ((1.0 - alpha) * self.ultimo_moveX)
                            moveY_f = (alpha * crudoY) + ((1.0 - alpha) * self.ultimo_moveY)
                            self.ultimo_moveX, self.ultimo_moveY = moveX_f, moveY_f
                            moveX, moveY = int(moveX_f), int(moveY_f)

                        if self.jugando:
                            # Limites de pantalla reforzados
                            self.cursor_x = max(15, min(785, self.cursor_x + moveX))
                            self.cursor_y = max(15, min(485, self.cursor_y + moveY))
                            self.dibujar_escena()

                            try:
                                with open(self.archivo_db, mode='a', newline='') as f:
                                    writer = csv.writer(f)
                                    writer.writerow([crudoX, crudoY, self.cursor_x, self.cursor_y, self.objetivo_x, self.objetivo_y, self.tipo_objetivo, comando_clic])
                            except PermissionError:
                                pass 

                            if comando_clic > 0:
                                # 1. DETECCIÓN DE SALIDA DE EMERGENCIA
                                if 680 < self.cursor_x < 790 and 10 < self.cursor_y < 50:
                                    self.on_closing()
                                    return 

                                # 2. DETECCIÓN DE OBJETIVO (Hitbox 65px)
                                dist = math.sqrt((self.cursor_x - self.objetivo_x)**2 + (self.cursor_y - self.objetivo_y)**2)
                                if dist < 65 and comando_clic == self.tipo_objetivo:
                                    self.generar_objetivo()
            except:
                pass

        # Solo repetimos el bucle si la ventana sigue existiendo
        if self.root.winfo_exists():
            self.root.after(10, self.bucle_principal)

    def on_closing(self):
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RecolectorIA(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()