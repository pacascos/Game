import sys
import os
import time
import math
import struct
import wave
import numpy as np
import pygame
import random
import subprocess

class Sonidos:
    def __init__(self):
        """Inicializa el sistema de sonido"""
        self.sonido_activo = True
        self.procesos_activos = []
        self.ultimo_sonido = 0  # Para control de frecuencia
        
        # Configurar sistema de sonido según plataforma
        if sys.platform == 'win32':
            self.metodo_reproduccion = self._reproducir_windows
        elif sys.platform == 'darwin':
            self.metodo_reproduccion = self._reproducir_mac
        else:
            self.metodo_reproduccion = self._reproducir_linux
        
        # Crear directorio de sonidos si no existe
        os.makedirs("sounds", exist_ok=True)
        
        # Generar sonidos si no existen
        self._generar_sonidos()
        
        # Cargar sonidos
        try:
            self.sonido_exito = pygame.mixer.Sound("sounds/exito.wav")
            self.sonido_explosion = pygame.mixer.Sound("sounds/explosion.wav")
            self.sonido_inicio = pygame.mixer.Sound("sounds/inicio.wav")
            self.sonido_precision = pygame.mixer.Sound("sounds/precision.wav")
        except Exception as e:
            print(f"Error cargando sonidos: {e}")
            self.sonido_activo = False
    
    def _generar_sonidos(self):
        """Genera todos los archivos de sonido necesarios"""
        sonidos = {
            "propulsor": (0.1, self._generar_ruido, {"volumen": 0.4}),
            "propulsor_lateral": (0.05, self._generar_ruido, {"volumen": 0.2}),
            "explosion": (1.0, self._generar_ruido, {"volumen": 0.7, "decay": True}),
            "exito": (1.0, self._generar_melodia, {"frecuencia": 440}),
            "inicio": (0.5, self._generar_barrido, {"frecuencia": 330}),
            "precision": (0.2, self._generar_tono, {"frecuencia": 660})
        }
        
        for nombre, (duracion, generador, params) in sonidos.items():
            archivo = f"sounds/{nombre}.wav"
            if not os.path.exists(archivo):
                buffer = generador(duracion, **params)
                self._guardar_wav(buffer, archivo)
    
    def _generar_ruido(self, duracion, volumen=1.0, decay=False):
        """Genera ruido blanco con volumen y decay opcionales"""
        samples = int(44100 * duracion)
        buffer = np.zeros(samples, dtype=np.int16)
        
        for i in range(samples):
            factor = math.exp(-3.0 * i / samples) if decay else 1.0
            valor = int(random.uniform(-32767, 32767) * volumen * factor)
            buffer[i] = valor
        
        return buffer
    
    def _generar_tono(self, duracion, frecuencia):
        """Genera un tono simple"""
        samples = int(44100 * duracion)
        t = np.linspace(0, duracion, samples)
        buffer = (np.sin(2 * np.pi * frecuencia * t) * 32767).astype(np.int16)
        return buffer
    
    def _generar_melodia(self, duracion, frecuencia):
        """Genera una melodía ascendente de éxito"""
        samples = int(44100 * duracion)
        t = np.linspace(0, duracion, samples)
        buffer = np.zeros(samples, dtype=np.int16)
        
        # Secuencia de notas más alegre
        notas = [frecuencia, frecuencia * 1.25, frecuencia * 1.5, frecuencia * 2]
        duracion_nota = samples // len(notas)
        
        for i, freq in enumerate(notas):
            inicio = i * duracion_nota
            fin = (i + 1) * duracion_nota
            t_nota = np.linspace(0, duracion/len(notas), duracion_nota)
            # Envolvente para suavizar transiciones
            env = np.sin(np.pi * t_nota / (duracion/len(notas)))
            buffer[inicio:fin] = (np.sin(2 * np.pi * freq * t_nota) * 32767 * env).astype(np.int16)
        
        return buffer
    
    def _generar_barrido(self, duracion, frecuencia):
        """Genera un barrido de frecuencia"""
        samples = int(44100 * duracion)
        t = np.linspace(0, duracion, samples)
        freq_mod = frecuencia * (1 + t)
        buffer = (np.sin(2 * np.pi * freq_mod * t) * 32767).astype(np.int16)
        return buffer
    
    def _guardar_wav(self, buffer, archivo):
        """Guarda un buffer de audio como archivo WAV"""
        with wave.open(archivo, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            wav.writeframes(buffer.tobytes())
    
    def _reproducir_mac(self, archivo):
        """Reproduce un sonido en macOS"""
        try:
            # Limpiar procesos terminados
            self.procesos_activos = [p for p in self.procesos_activos if p.poll() is None]
            
            # Verificar que el archivo existe
            if not os.path.exists(archivo):
                return False
            
            proceso = subprocess.Popen(['afplay', archivo],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
            self.procesos_activos.append(proceso)
            return True
        except:
            return False
    
    def reproducir_sonido(self, nombre, intervalo=0):
        """Reproduce un sonido con control de frecuencia opcional"""
        if not self.sonido_activo:
            return
            
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_sonido < intervalo:
            return
            
        self.ultimo_sonido = tiempo_actual
        self.metodo_reproduccion(f"sounds/{nombre}.wav")
    
    # Métodos públicos simplificados
    def reproducir_propulsor(self):
        self.reproducir_sonido("propulsor", 100)
    
    def reproducir_propulsor_lateral(self):
        self.reproducir_sonido("propulsor_lateral", 100)
    
    def reproducir_explosion(self):
        self.reproducir_sonido("explosion")
    
    def reproducir_exito(self):
        """Reproduce el sonido de éxito"""
        if not self.sonido_activo:
            return
        # Reproducir sin intervalo y esperar un poco
        self.reproducir_sonido("exito", 0)
        # Dar tiempo para que el sonido comience
        time.sleep(0.1)
    
    def reproducir_inicio(self):
        self.reproducir_sonido("inicio")
    
    def reproducir_precision(self):
        self.reproducir_sonido("precision")
    
    def detener_todos(self):
        """Detiene todos los sonidos activos"""
        for proceso in self.procesos_activos:
            try:
                proceso.terminate()
            except:
                pass
        self.procesos_activos = []
    
    def __del__(self):
        self.detener_todos()