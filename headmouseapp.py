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
import threading
import subprocess # NUEVA LIBRERÍA: Para abrir otros programas
import os
import customtkinter as ctk
import keyboard

BAUD_RATE = 115200
pyautogui.PAUSE = 0.0
pyautogui.FAILSAFE = False

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  

class HeadMouseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HeadMouse Control Center")
        self.geometry("650x650")
        self.resizable(False, False)

        self.puerto_detectado = None
        self.arduino = None
        self.corriendo = False
        self.modo_actual = "Escritorio"
        self.calibrando = False

        self.ultimo_moveX = 0.0
        self.ultimo_moveY = 0.0

        self.crear_interfaz()
        keyboard.add_hotkey('ctrl+shift+c', self.iniciar_calibracion_hilo)

        threading.Thread(target=self.buscar_y_conectar, daemon=True).start()

    def crear_interfaz(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10, border_width=2, border_color="#2980B9")
        self.header_frame.pack(pady=(15, 10), padx=20, fill="x")

        self.lbl_title = ctk.CTkLabel(self.header_frame, text="HEADMOUSE™", font=ctk.CTkFont(size=36, weight="bold", family="Roboto"), text_color="#3498DB")
        self.lbl_title.pack(pady=(10, 0))
        
        self.lbl_subtitle = ctk.CTkLabel(self.header_frame, text="BY HECTOR VIEIRA 21-00290 USB PROYECT", font=ctk.CTkFont(size=11, weight="bold"), text_color="#7F8C8D")
        self.lbl_subtitle.pack(pady=(0, 10))

        self.status_frame = ctk.CTkFrame(self, corner_radius=8)
        self.status_frame.pack(pady=5, padx=20, fill="x")

        self.lbl_status = ctk.CTkLabel(self.status_frame, text="Buscando dispositivo USB...", font=ctk.CTkFont(size=16, weight="bold"), text_color="#F1C40F")
        self.lbl_status.pack(pady=10)

        self.control_frame = ctk.CTkFrame(self, corner_radius=8, border_width=1, border_color="#34495E")
        self.control_frame.pack(pady=10, padx=20, fill="x")
        
        self.lbl_modos = ctk.CTkLabel(self.control_frame, text="⚙️ Perfiles de Operación", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_modos.pack(pady=(10, 5))

        self.seg_modos = ctk.CTkSegmentedButton(self.control_frame, values=["Escritorio", "Gaming", "Películas", "Entrenar IA"], command=self.cambiar_modo, height=35)
        self.seg_modos.set("Escritorio")
        self.seg_modos.pack(pady=(0, 15), padx=20, fill="x")

        self.calib_frame = ctk.CTkFrame(self, corner_radius=8, fg_color="#2C3E50")
        self.calib_frame.pack(pady=5, padx=20, fill="x")

        self.lbl_calib = ctk.CTkLabel(self.calib_frame, text="🎯 Calibración de Precisión", font=ctk.CTkFont(size=14, weight="bold"), text_color="white")
        self.lbl_calib.pack(pady=(10, 5))

        self.btn_calibrar = ctk.CTkButton(self.calib_frame, text="Recalibrar Centro (Ctrl+Shift+C)", height=45, font=ctk.CTkFont(weight="bold"), fg_color="#E67E22", hover_color="#D35400", command=self.iniciar_calibracion_hilo)
        self.btn_calibrar.pack(pady=(5, 5), padx=20, fill="x")
        
        self.progress_bar = ctk.CTkProgressBar(self.calib_frame, height=10, progress_color="#2ECC71")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(0, 15), padx=20, fill="x")

        self.log_box = ctk.CTkTextbox(self, height=100, state="disabled", font=ctk.CTkFont(family="Consolas", size=12), fg_color="#111111", text_color="#2ECC71")
        self.log_box.pack(pady=10, padx=20, fill="both", expand=True)
        self.log("Sistema Iniciado. Esperando hardware...")

    def log(self, mensaje):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"> {mensaje}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def cambiar_modo(self, nuevo_modo):
        modo_anterior = self.modo_actual
        self.modo_actual = nuevo_modo
        self.log(f"Perfil cambiado a: {nuevo_modo}")

        # === ARQUITECTURA MASTER HUB (LANZAMIENTO DE IA) ===
        if nuevo_modo == "Entrenar IA":
            self.lbl_status.configure(text="En Línea - MODO ENTRENAMIENTO (Standby)", text_color="#3498DB")
            self.log("Liberando puerto USB para cederlo al minijuego...")
            
            # Soltamos el Arduino
            if self.arduino and self.arduino.is_open:
                self.arduino.close()
            
            self.log("Lanzando Entrenador_IA.py...")
            try:
                # Calculamos la ruta absoluta exacta para evitar el error de System32
                directorio_actual = os.path.dirname(os.path.abspath(__file__))
                ruta_entrenador = os.path.join(directorio_actual, "Entrenador_IA.py")
                
                # Lanzamos el programa usando la ruta completa
                subprocess.Popen([sys.executable, ruta_entrenador])
                self.log("¡Juego abierto! Vuelve a seleccionar 'Escritorio' al terminar.")
            
            except Exception as e:
                # SI FALLA: Recuperamos el mouse automáticamente para no dejarte atascado
                self.log(f"Error al abrir el juego: {e}")
                self.log("Activando protocolo de seguridad: Recuperando puerto...")
                self.seg_modos.set("Escritorio")
                self.cambiar_modo("Escritorio") # Forzamos el regreso

        else:
            # Si venimos de Entrenar IA y queremos volver a usar el mouse normal
            if modo_anterior == "Entrenar IA":
                self.log("Recuperando el puerto USB...")
                if self.arduino and not self.arduino.is_open:
                    try:
                        # Le damos 1 segundo al SO para que libere el puerto completamente
                        time.sleep(1) 
                        self.arduino.open()
                        time.sleep(1.5)
                        self.arduino.flushInput()
                        self.log("Puerto recuperado exitosamente.")
                    except Exception as e:
                        self.log(f"Error al reconectar puerto: {e}")

            if nuevo_modo == "Películas":
                self.lbl_status.configure(text="En Línea - MODO PELÍCULAS (Standby)", text_color="#9B59B6")
            elif nuevo_modo == "Gaming":
                self.lbl_status.configure(text="En Línea - MODO GAMING (Baja Latencia)", text_color="#E74C3C")
                self.ultimo_moveX = 0
                self.ultimo_moveY = 0
            else:
                self.lbl_status.configure(text="En Línea - MODO ESCRITORIO (IA Activa)", text_color="#2ECC71")

    def iniciar_calibracion_hilo(self):
        if not self.calibrando and self.puerto_detectado and self.modo_actual != "Entrenar IA":
            threading.Thread(target=self.rutina_calibracion, daemon=True).start()

    def rutina_calibracion(self):
        self.calibrando = True
        self.btn_calibrar.configure(state="disabled", fg_color="#7F8C8D")
        
        screen_w, screen_h = pyautogui.size()
        centro_x = screen_w / 2
        centro_y = screen_h / 2
        
        pyautogui.moveTo(centro_x, centro_y)
        self.log("Cursor bloqueado. ¡Mira la flecha!")

        for i in range(5, 0, -1):
            self.lbl_status.configure(text=f"Ajusta postura... {i}s", text_color="#E74C3C")
            self.progress_bar.set((5 - i) / 5.0)
            pyautogui.moveTo(centro_x, centro_y) 
            time.sleep(1)

        self.progress_bar.set(1.0)
        self.lbl_status.configure(text="¡QUÉDATE INMÓVIL! Muestreando...", text_color="#F39C12")

        if self.arduino and self.arduino.is_open:
            self.arduino.write(b'C') 
            esperando = True
            while esperando:
                if self.arduino.in_waiting > 0:
                    respuesta = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                    if "EXITOSA" in respuesta:
                        esperando = False

        self.log("Calibración Profunda Exitosa.")
        self.cambiar_modo(self.modo_actual) 
        self.btn_calibrar.configure(state="normal", text="Recalibrar Centro (Ctrl+Shift+C)", fg_color="#E67E22")
        self.progress_bar.set(0)
        self.calibrando = False

    def buscar_y_conectar(self):
        self.log("Buscando puertos...")
        puertos = [p for p in serial.tools.list_ports.comports() if "Bluetooth" not in p.description]
        
        for puerto in puertos:
            try:
                prueba = serial.Serial(puerto.device, BAUD_RATE, timeout=0.5)
                time.sleep(1) 
                for _ in range(4):
                    linea = prueba.readline().decode('utf-8', errors='ignore').strip()
                    if "CALIBRANDO" in linea or "EXITOSA" in linea:
                        self.puerto_detectado = puerto.device
                        prueba.close()
                        break
                prueba.close()
            except Exception: pass
            if self.puerto_detectado: break

        if self.puerto_detectado:
            self.lbl_status.configure(text=f"Detectado en {self.puerto_detectado}", text_color="#3498DB")
            self.iniciar_driver_mouse()
        else:
            self.lbl_status.configure(text="Dispositivo no encontrado", text_color="#E74C3C")

    def iniciar_driver_mouse(self):
        try:
            self.arduino = serial.Serial(self.puerto_detectado, BAUD_RATE, timeout=0.1)
            time.sleep(2)
            self.arduino.flushInput()
            
            self.cambiar_modo(self.modo_actual)
            self.corriendo = True
            
            while self.corriendo:
                # Si estamos calibrando O si le dimos el puerto al juego, no leemos
                if self.calibrando or self.modo_actual == "Entrenar IA":
                    time.sleep(0.1)
                    continue

                if self.arduino.in_waiting > 0:
                    linea = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                    if not linea or "CALIB" in linea or "EXITOSA" in linea: continue
                        
                    try:
                        datos = linea.split(',')
                        if len(datos) == 3:
                            crudoX = float(datos[0])
                            crudoY = float(datos[1])
                            comando_clic = int(datos[2])
                            
                            if self.modo_actual == "Películas":
                                continue 
                                
                            if crudoX == 0 and crudoY == 0:
                                self.ultimo_moveX = 0
                                self.ultimo_moveY = 0
                                moveX, moveY = 0, 0
                            elif self.modo_actual == "Gaming":
                                moveX = int(crudoX)
                                moveY = int(crudoY)
                            elif self.modo_actual == "Escritorio":
                                velocidad = (abs(crudoX) + abs(crudoY))
                                factor_alpha = 0.15 if velocidad < 15 else 0.8
                                moveX_float = (factor_alpha * crudoX) + ((1.0 - factor_alpha) * self.ultimo_moveX)
                                moveY_float = (factor_alpha * crudoY) + ((1.0 - factor_alpha) * self.ultimo_moveY)
                                self.ultimo_moveX = moveX_float
                                self.ultimo_moveY = moveY_float
                                moveX = int(moveX_float)
                                moveY = int(moveY_float)

                            if moveX != 0 or moveY != 0:
                                pyautogui.moveRel(moveX, moveY)
                            
                            if comando_clic == 1:
                                pyautogui.click(button='left')
                            elif comando_clic == 2:
                                pyautogui.click(button='right')
                            elif comando_clic == 3:
                                pyautogui.doubleClick()
                                
                    except ValueError: pass

        except Exception as e:
            self.log(f"Error crítico en bucle: {e}")
            self.lbl_status.configure(text="Conexión Perdida", text_color="#E74C3C")

    def on_closing(self):
        self.corriendo = False
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    try:
        app = HeadMouseApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        import traceback
        print("\n❌ ERROR CRÍTICO ❌\n")
        traceback.print_exc()
        input("Presiona ENTER para salir...")