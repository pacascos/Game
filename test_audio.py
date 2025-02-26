import pygame
import sys
import numpy as np
import time

print("\n=== TEST DE AUDIO INDEPENDIENTE ===")
print("Python version:", sys.version)
print("Pygame version:", pygame.version.ver)

# Forzar la salida inmediata (sin buffer)
import functools
print = functools.partial(print, flush=True)

print("Iniciando pygame...")
pygame.init()
print("Pygame inicializado.")

print("Estado del mixer antes de init:", pygame.mixer.get_init())

try:
    print("Intentando inicializar el mixer...")
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=2048)
    print("Mixer inicializado con éxito.")
    print("Estado del mixer:", pygame.mixer.get_init())
    print("Canales disponibles:", pygame.mixer.get_num_channels())
    
    print("\nCreando sonido de prueba...")
    # Creando un sonido simple (un beep)
    buffer = np.zeros((22050, 2), dtype=np.int16)
    t = np.linspace(0, 1, 22050)
    buffer[:, 0] = (np.sin(2 * np.pi * 440 * t) * 32000).astype(np.int16)  # Nota LA (440 Hz)
    buffer[:, 1] = buffer[:, 0]
    
    print("Creando objeto de sonido...")
    sonido = pygame.sndarray.make_sound(buffer)
    
    print("Configurando volumen máximo...")
    sonido.set_volume(1.0)
    
    print("\n¡REPRODUCIENDO SONIDO DE PRUEBA!")
    print("Deberías escuchar un beep de 1 segundo...")
    canal = sonido.play()
    print(f"Reproduciendo en canal: {canal}")
    
    # Esperar a que termine el sonido
    print("Esperando a que termine el sonido...")
    time.sleep(2)
    
    print("\nPrueba finalizada. Si no escuchaste ningún sonido, hay un problema con:")
    print("1. El sistema de sonido de tu computadora")
    print("2. La configuración de pygame.mixer")
    print("3. Los drivers de audio")

except Exception as e:
    print(f"ERROR al inicializar el mixer: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIN DEL TEST DE AUDIO ===") 