import sys
import os
import time
import math
import struct
import wave

class Sonidos:
    def __init__(self):
        self.propulsor_sonando = False
        self.propulsor_lateral_sonando = False
        
        print("Inicializando sistema de sonido simple...")
        
        # Determinar método para reproducir sonidos según sistema operativo
        if sys.platform == 'win32':
            self.metodo_reproduccion = self._reproducir_windows
            print("Modo de reproducción: Windows")
        elif sys.platform == 'darwin':  # macOS
            self.metodo_reproduccion = self._reproducir_mac
            print("Modo de reproducción: macOS")
        else:  # Linux y otros
            self.metodo_reproduccion = self._reproducir_linux
            print("Modo de reproducción: Linux")
        
        # Crear directorio para sonidos si no existe
        if not os.path.exists("sounds"):
            os.makedirs("sounds", exist_ok=True)
            print("Directorio 'sounds' creado")
        
        # Crear archivos WAV si no existen
        self._crear_sonidos_wav()
    
    def _crear_sonidos_wav(self):
        """Crea todos los archivos WAV necesarios"""
        sonidos = {
            "propulsor": {"freq": 150, "duracion": 1.0},
            "propulsor_lateral": {"freq": 200, "duracion": 0.8},
            "explosion": {"freq": 100, "duracion": 1.5, "tipo": "ruido"},
            "exito": {"freq": 440, "duracion": 1.0, "tipo": "melodia"},
            "inicio": {"freq": 330, "duracion": 1.2, "tipo": "barrido"},
            "precision": {"freq": 660, "duracion": 0.5}
        }
        
        print("Verificando archivos de sonido...")
        for nombre, params in sonidos.items():
            ruta = f"sounds/{nombre}.wav"
            if not os.path.exists(ruta):
                tipo = params.get("tipo", "tono")
                print(f"Creando sonido '{nombre}.wav'...")
                if tipo == "ruido":
                    self._generar_wav_ruido(ruta, params["duracion"])
                elif tipo == "melodia":
                    self._generar_wav_melodia(ruta, params["freq"], params["duracion"])
                elif tipo == "barrido":
                    self._generar_wav_barrido(ruta, params["freq"], params["duracion"])
                else:
                    self._generar_wav_tono(ruta, params["freq"], params["duracion"])
        print("Verificación de sonidos completada")
    
    def _generar_wav_tono(self, ruta, frecuencia, duracion):
        """Genera un archivo WAV con un tono simple"""
        # Configuración WAV básica
        frames_segundo = 44100
        n_frames = int(duracion * frames_segundo)
        
        # Crear archivo WAV
        with wave.open(ruta, 'w') as archivo_wav:
            archivo_wav.setnchannels(1)  # Mono
            archivo_wav.setsampwidth(2)  # 2 bytes por muestra
            archivo_wav.setframerate(frames_segundo)
            
            # Generar onda sinusoidal simple
            for i in range(n_frames):
                # Generar valor con envolvente para evitar clics
                envolvente = 1.0 if i > 100 and i < n_frames - 100 else min(i/100.0, (n_frames-i)/100.0)
                valor = int(32767 * math.sin(2 * math.pi * frecuencia * i / frames_segundo) * envolvente)
                datos = struct.pack('h', valor)  # 'h' es para short (16 bits)
                archivo_wav.writeframesraw(datos)
    
    def _generar_wav_ruido(self, ruta, duracion):
        """Genera un archivo WAV con ruido (para explosión)"""
        import random
        
        frames_segundo = 44100
        n_frames = int(duracion * frames_segundo)
        
        with wave.open(ruta, 'w') as archivo_wav:
            archivo_wav.setnchannels(1)
            archivo_wav.setsampwidth(2)
            archivo_wav.setframerate(frames_segundo)
            
            for i in range(n_frames):
                # Ruido con envolvente decreciente
                envolvente = math.exp(-3.0 * i / n_frames)
                valor = int(random.uniform(-32767, 32767) * envolvente)
                datos = struct.pack('h', valor)
                archivo_wav.writeframesraw(datos)
    
    def _generar_wav_melodia(self, ruta, freq_base, duracion):
        """Genera un archivo WAV con una melodía ascendente (para éxito)"""
        frames_segundo = 44100
        n_frames = int(duracion * frames_segundo)
        
        with wave.open(ruta, 'w') as archivo_wav:
            archivo_wav.setnchannels(1)
            archivo_wav.setsampwidth(2)
            archivo_wav.setframerate(frames_segundo)
            
            # Melodía de tres notas
            notas = [freq_base, freq_base * 1.25, freq_base * 1.5]
            duracion_nota = n_frames // 3
            
            for i in range(n_frames):
                # Determinar qué nota estamos tocando
                idx_nota = min(i // duracion_nota, 2)
                freq = notas[idx_nota]
                
                # Calcular posición dentro de la nota actual
                pos_nota = i % duracion_nota
                env_nota = math.sin(math.pi * pos_nota / duracion_nota)
                
                valor = int(32767 * math.sin(2 * math.pi * freq * i / frames_segundo) * env_nota)
                datos = struct.pack('h', valor)
                archivo_wav.writeframesraw(datos)
    
    def _generar_wav_barrido(self, ruta, freq_inicio, duracion):
        """Genera un archivo WAV con un barrido de frecuencia (para inicio)"""
        frames_segundo = 44100
        n_frames = int(duracion * frames_segundo)
        
        with wave.open(ruta, 'w') as archivo_wav:
            archivo_wav.setnchannels(1)
            archivo_wav.setsampwidth(2)
            archivo_wav.setframerate(frames_segundo)
            
            for i in range(n_frames):
                # Frecuencia ascendente
                t = i / n_frames
                freq = freq_inicio + (freq_inicio * 1.5) * t
                
                # Envolvente que crece y luego disminuye
                env = math.sin(math.pi * t)
                
                valor = int(32767 * math.sin(2 * math.pi * freq * i / frames_segundo) * env)
                datos = struct.pack('h', valor)
                archivo_wav.writeframesraw(datos)
    
    def _reproducir_windows(self, archivo):
        """Reproduce un sonido en Windows"""
        import winsound
        try:
            winsound.PlaySound(archivo, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except Exception as e:
            print(f"Error reproduciendo sonido en Windows: {e}")
            return False
    
    def _reproducir_mac(self, archivo):
        """Reproduce un sonido en macOS"""
        try:
            os.system(f"afplay {archivo} &")
            return True
        except Exception as e:
            print(f"Error reproduciendo sonido en macOS: {e}")
            return False
    
    def _reproducir_linux(self, archivo):
        """Reproduce un sonido en Linux"""
        try:
            os.system(f"aplay {archivo} &> /dev/null &")
            return True
        except Exception as e:
            print(f"Error reproduciendo sonido en Linux: {e}")
            return False
    
    # Métodos públicos para reproducción
    def reproducir_propulsor(self):
        if not self.propulsor_sonando:
            self.propulsor_sonando = True
            self.metodo_reproduccion("sounds/propulsor.wav")
    
    def detener_propulsor(self):
        self.propulsor_sonando = False
        # La detención depende del sistema operativo y es compleja
        # En esta versión simple, dejamos que los sonidos terminen por sí solos
    
    def reproducir_propulsor_lateral(self):
        if not self.propulsor_lateral_sonando:
            self.propulsor_lateral_sonando = True
            self.metodo_reproduccion("sounds/propulsor_lateral.wav")
    
    def detener_propulsor_lateral(self):
        self.propulsor_lateral_sonando = False
    
    def reproducir_explosion(self):
        self.metodo_reproduccion("sounds/explosion.wav")
    
    def reproducir_exito(self):
        self.metodo_reproduccion("sounds/exito.wav")
    
    def reproducir_inicio(self):
        self.metodo_reproduccion("sounds/inicio.wav")
    
    def reproducir_precision(self):
        self.metodo_reproduccion("sounds/precision.wav")
    
    def detener_todos(self):
        self.propulsor_sonando = False
        self.propulsor_lateral_sonando = False
        # No hay una forma simple de detener todos los sonidos en todos los sistemas operativos
        # En esta versión simple, dejamos que los sonidos terminen naturalmente 