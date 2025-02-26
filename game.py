import pygame
import sys
from math import cos, sin, radians
import random
from scores import TableroRecords
import datetime
import math
from sonidos import Sonidos
import subprocess

# Inicialización de Pygame
pygame.init()

# Constantes
ANCHO = 800
ALTO = 600
FPS = 60
GRAVEDAD = 0.03
EMPUJE = 0.1
EMPUJE_LATERAL = 0.08
VIENTO_MAX = 0.025     # Reducido de 0.03 a 0.02
CAMBIO_VIENTO = 0.02   # Reducido de 0.2 a 0.02 (10 veces menos frecuente)
VIENTO_INCREMENTO = 0.001  # Nueva constante para cambio gradual
FUEL_INICIAL = 400
COLOR_BLANCO = (255, 255, 255)
COLOR_ROJO = (255, 0, 0)
COLOR_VERDE = (0, 255, 0)
COLOR_AMARILLO = (255, 255, 0)
COLOR_AZUL = (0, 191, 255)
BASE_ANCHO = 60  # Ancho de la base de aterrizaje
BASE_X = ANCHO // 2  # Posición X de la base (centro)
VELOCIDAD_MAXIMA_ATERRIZAJE = 3.0  # Nueva constante para velocidad máxima de aterrizaje
ESTRELLAS_CANTIDAD = 100
COLOR_FUEGO = [(255, 165, 0), (255, 69, 0), (255, 0, 0)]  # Degradado de fuego
COLOR_GRIS = (128, 128, 128)
COLOR_NEGRO = (0, 0, 0)
PARTICULAS_EXPLOSION = 80  # Aumentado de 50 a 80
PARTICULAS_EXITO = 30
COLOR_FUEGO_EXPLOSION = [(255, 200, 0), (255, 100, 0), (255, 0, 0)]
COLOR_EXITO = [(255, 215, 0), (0, 255, 0), (255, 255, 255)]
BASE_ALTURA_SOBRE_SUELO = 30  # Altura de la base sobre la superficie lunar
SUELO_ALTURA = 50  # Altura del suelo lunar (ya existente como valor fijo, ahora como constante)
PARTICULAS_EXPLOSION_SECUNDARIAS = 40  # Para la segunda fase de la explosión
COLOR_HUMO_EXPLOSION = [(150, 150, 150), (100, 100, 100), (80, 80, 80)]  # Colores para el humo
COLOR_DESTELLO = [(255, 255, 200), (255, 255, 255)]  # Para el destello inicial

# Nuevas constantes para mejorar la jugabilidad
MODO_PRECISION = 0.5  # Factor de reducción del empuje en modo precisión
INDICADOR_ATERRIZAJE = True  # Mostrar indicador de zona segura
GRAVEDAD = 0.03  # Gravedad lunar constante para todos los niveles

FUEL_POR_NIVEL = {  # Combustible según el nivel
    1: 500,    # Nivel fácil: mucho combustible
    2: 300,    # Nivel medio: combustible moderado
    3: 150     # Nivel difícil: poco combustible
}

VIENTO_POR_NIVEL = {  # Intensidad del viento según el nivel
    1: 0.01,   # Nivel fácil: viento muy suave
    2: 0.03,   # Nivel medio: viento moderado
    3: 0.05    # Nivel difícil: viento fuerte
}

# Configuración de la pantalla
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Aterrizaje Lunar")
reloj = pygame.time.Clock()

class Base:
    def __init__(self, nivel=1):
        self.ancho = BASE_ANCHO
        self.alto = 20
        
        # Determinar rango de posición según nivel
        margen = 100  # Margen mínimo desde los bordes
        if nivel == 1:
            # Nivel fácil: Base cerca del centro (±20% del espacio disponible)
            desplazamiento_max = (ANCHO - 2*margen) * 0.2
        elif nivel == 2:
            # Nivel medio: Base más alejada (±40% del espacio disponible)
            desplazamiento_max = (ANCHO - 2*margen) * 0.4
        else:
            # Nivel difícil: Base puede estar casi en cualquier lugar (±70% del espacio disponible)
            desplazamiento_max = (ANCHO - 2*margen) * 0.7
        
        # Posición aleatoria dentro del rango permitido
        desplazamiento = random.uniform(-desplazamiento_max, desplazamiento_max)
        self.x = ANCHO//2 + desplazamiento
        
        # Asegurar que la base no quede muy cerca de los bordes
        self.x = max(margen + self.ancho//2, min(ANCHO - margen - self.ancho//2, self.x))
        
        self.y = ALTO - SUELO_ALTURA - BASE_ALTURA_SOBRE_SUELO
        
        # Ajustar posición de la manga de viento
        self.manga_x = self.x - self.ancho//2 - 40
        self.manga_y = self.y - 80

    def dibujar(self, viento):
        # Dibujar pilares de soporte desde el suelo
        altura_pilares = BASE_ALTURA_SOBRE_SUELO + self.alto
        ancho_pilar = 8
        
        # Pilares principales
        for x_pilar in [self.x - self.ancho//3, self.x + self.ancho//3]:
            # Pilar con degradado
            for i in range(altura_pilares):
                oscuridad = max(100, 150 - i//2)  # Más oscuro abajo, más claro arriba
                pygame.draw.rect(pantalla, (oscuridad, oscuridad, oscuridad),
                               (x_pilar - ancho_pilar//2, 
                                self.y + self.alto + i, 
                                ancho_pilar, 1))
        
        # Soportes diagonales
        for x_offset in [-self.ancho//3, self.ancho//3]:
            puntos_soporte = [
                (self.x + x_offset, self.y + self.alto),  # Punto superior
                (self.x + x_offset * 1.5, ALTO - SUELO_ALTURA),  # Punto inferior exterior
                (self.x + x_offset * 1.3, ALTO - SUELO_ALTURA),  # Punto inferior interior
                (self.x + x_offset * 0.8, self.y + self.alto + 5)  # Punto superior interior
            ]
            pygame.draw.polygon(pantalla, COLOR_GRIS, puntos_soporte)
            pygame.draw.polygon(pantalla, (100, 100, 100), puntos_soporte, 1)
        
        # Detalles de la plataforma
        # Líneas de advertencia
        for i in range(4):
            x_pos = self.x - self.ancho//2 + (i * self.ancho//3)
            pygame.draw.rect(pantalla, COLOR_AMARILLO,
                           (x_pos, self.y, self.ancho//6, self.alto))
            pygame.draw.rect(pantalla, COLOR_NEGRO,
                           (x_pos, self.y, self.ancho//6, self.alto), 1)
        
        # Borde de la plataforma
        pygame.draw.rect(pantalla, COLOR_GRIS,
                        (self.x - self.ancho//2, self.y, self.ancho, self.alto), 2)
        
        # Luces de la plataforma
        for x in [self.x - self.ancho//3, self.x, self.x + self.ancho//3]:
            pygame.draw.circle(pantalla, COLOR_ROJO, (int(x), int(self.y + self.alto//2)), 3)
        
        # Estructura de soporte
        pata_ancho = 15
        pata_alto = 35
        
        # Dibujar estructura central
        pygame.draw.rect(pantalla, COLOR_GRIS,
                        (self.x - pata_ancho, self.y + self.alto,
                         pata_ancho * 2, pata_alto))
        
        # Detalles técnicos (tubos, conectores, etc.)
        for y_offset in range(5, pata_alto - 5, 10):
            pygame.draw.line(pantalla, COLOR_BLANCO,
                           (self.x - pata_ancho + 3, self.y + self.alto + y_offset),
                           (self.x + pata_ancho - 3, self.y + self.alto + y_offset), 1)
        
        # Mástil de la manga mejorado
        mastil_ancho = 6
        mastil_alto = 90
        
        # Base del mástil más elaborada
        pygame.draw.polygon(pantalla, COLOR_GRIS, [
            (self.manga_x - 8, self.manga_y + mastil_alto),
            (self.manga_x + mastil_ancho + 8, self.manga_y + mastil_alto),
            (self.manga_x + mastil_ancho + 12, self.manga_y + mastil_alto + 15),
            (self.manga_x - 12, self.manga_y + mastil_alto + 15)
        ])
        
        # Mástil con detalles
        pygame.draw.rect(pantalla, COLOR_GRIS,
                        (self.manga_x, self.manga_y, mastil_ancho, mastil_alto))
        
        # Detalles del mástil
        for y in range(self.manga_y + 10, self.manga_y + mastil_alto, 20):
            pygame.draw.rect(pantalla, COLOR_BLANCO,
                           (self.manga_x - 1, y, mastil_ancho + 2, 2))
        
        # Manga con mejor diseño
        manga_longitud = 50
        manga_deflexion = int(manga_longitud * (viento / VIENTO_MAX))
        
        # Dibujar manga con efecto de volumen
        puntos_manga = [
            (self.manga_x + mastil_ancho, self.manga_y + 10),
            (self.manga_x + mastil_ancho + manga_deflexion, self.manga_y + 15),
            (self.manga_x + mastil_ancho + manga_deflexion * 1.2, self.manga_y + 25),
            (self.manga_x + mastil_ancho + manga_deflexion, self.manga_y + 35),
            (self.manga_x + mastil_ancho, self.manga_y + 40)
        ]
        
        # Efecto de volumen en la manga
        pygame.draw.polygon(pantalla, COLOR_ROJO, puntos_manga)
        pygame.draw.polygon(pantalla, (200, 0, 0), puntos_manga, 0)  # Sombreado
        pygame.draw.polygon(pantalla, COLOR_BLANCO, puntos_manga, 2)  # Borde
        
        # Líneas de detalle en la manga
        for i in range(1, 3):
            y_offset = i * 10
            pygame.draw.line(pantalla, COLOR_BLANCO,
                           (self.manga_x + mastil_ancho, self.manga_y + 10 + y_offset),
                           (self.manga_x + mastil_ancho + manga_deflexion * 0.8,
                            self.manga_y + 10 + y_offset), 1)

class Estrellas:
    def __init__(self):
        self.estrellas = [(random.randint(0, ANCHO), 
                          random.randint(0, ALTO - 50),
                          random.random() * 2 + 1) for _ in range(ESTRELLAS_CANTIDAD)]
    
    def dibujar(self):
        for x, y, tamaño in self.estrellas:
            pygame.draw.circle(pantalla, COLOR_BLANCO, (int(x), int(y)), int(tamaño))

class Particula:
    def __init__(self, x, y, color, velocidad_x, velocidad_y, vida, tamaño):
        self.x = x
        self.y = y
        self.color = color
        self.velocidad_x = velocidad_x
        self.velocidad_y = velocidad_y
        self.vida = vida
        self.vida_inicial = vida
        self.tamaño = tamaño

    def actualizar(self):
        self.x += self.velocidad_x
        self.y += self.velocidad_y
        self.vida -= 1
        self.velocidad_y += 0.1  # Gravedad
        return self.vida > 0

    def dibujar(self, pantalla):
        alpha = int(255 * (self.vida / self.vida_inicial))
        color = list(self.color)
        # Crear una superficie temporal para el efecto de transparencia
        surf = pygame.Surface((self.tamaño * 2, self.tamaño * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, alpha), (self.tamaño, self.tamaño), self.tamaño)
        pantalla.blit(surf, (int(self.x - self.tamaño), int(self.y - self.tamaño)))

class EfectosVisuales:
    def __init__(self):
        self.particulas = []
        self.particulas_secundarias = []  # Para humo y residuos
        self.activo = False
        self.tiempo_explosion = 0
        self.onda_expansion = None  # Para la onda expansiva

    def crear_explosion(self, x, y):
        self.particulas = []
        self.particulas_secundarias = []
        self.tiempo_explosion = 30  # Duración del destello inicial
        
        # Efecto de destello inicial (partículas grandes y brillantes)
        for _ in range(15):
            angulo = random.uniform(0, 2 * math.pi)
            velocidad = random.uniform(1, 4)
            velocidad_x = math.cos(angulo) * velocidad
            velocidad_y = math.sin(angulo) * velocidad
            color = random.choice(COLOR_DESTELLO)
            tamaño = random.randint(10, 20)
            vida = random.randint(10, 20)
            self.particulas.append(Particula(x, y, color, velocidad_x, velocidad_y, vida, tamaño))
        
        # Partículas principales de fuego (más numerosas y variadas)
        for _ in range(PARTICULAS_EXPLOSION):
            angulo = random.uniform(0, 2 * math.pi)
            velocidad = random.uniform(2, 10)  # Más variación en velocidad
            velocidad_x = math.cos(angulo) * velocidad
            velocidad_y = math.sin(angulo) * velocidad
            color = random.choice(COLOR_FUEGO_EXPLOSION)
            tamaño = random.randint(3, 8)  # Más variación en tamaño
            vida = random.randint(20, 50)  # Más variación en vida
            self.particulas.append(Particula(x, y, color, velocidad_x, velocidad_y, vida, tamaño))
        
        # Partículas de humo (más lentas y duraderas)
        for _ in range(PARTICULAS_EXPLOSION_SECUNDARIAS):
            angulo = random.uniform(0, 2 * math.pi)
            velocidad = random.uniform(1, 3)
            velocidad_x = math.cos(angulo) * velocidad
            velocidad_y = math.sin(angulo) * velocidad - 0.5  # Tendencia a subir
            color = random.choice(COLOR_HUMO_EXPLOSION)
            tamaño = random.randint(4, 10)
            vida = random.randint(60, 120)  # Más duradero
            self.particulas_secundarias.append(Particula(x, y, color, velocidad_x, velocidad_y, vida, tamaño))
        
        # Crear onda expansiva
        self.onda_expansion = {
            'x': x,
            'y': y,
            'radio': 5,
            'max_radio': 50,
            'vida': 20
        }
        
        self.activo = True

    def actualizar_y_dibujar(self, pantalla):
        if not self.activo:
            return
            
        # Actualizar y dibujar onda expansiva
        if self.onda_expansion is not None:
            self.onda_expansion['radio'] += 8
            self.onda_expansion['vida'] -= 1
            
            if self.onda_expansion['vida'] > 0:
                # Asegurarnos que alpha está en el rango correcto (0-255)
                alpha = max(0, min(255, int(255 * (self.onda_expansion['vida'] / 20))))
                # Crear color con alpha como cuarto componente
                color_onda = (255, 200, 50, alpha)
                
                # Crear superficie transparente y dibujar círculo
                surf = pygame.Surface((self.onda_expansion['radio'] * 2, self.onda_expansion['radio'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    surf, 
                    color_onda,
                    (self.onda_expansion['radio'], self.onda_expansion['radio']), 
                    self.onda_expansion['radio'],
                    3  # Grosor de la línea
                )
                
                pantalla.blit(
                    surf, 
                    (int(self.onda_expansion['x'] - self.onda_expansion['radio']), 
                     int(self.onda_expansion['y'] - self.onda_expansion['radio']))
                )
            else:
                self.onda_expansion = None
        
        # Actualizar tiempo destello
        if self.tiempo_explosion > 0:
            # Crear efecto de destello
            surf = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            alpha = int(100 * (self.tiempo_explosion / 30))
            surf.fill((255, 255, 200, alpha))
            pantalla.blit(surf, (0, 0))
            self.tiempo_explosion -= 1
        
        # Actualizar partículas primarias (fuego)
        particulas_activas = []
        for particula in self.particulas:
            if particula.actualizar():
                particulas_activas.append(particula)
                particula.dibujar(pantalla)
        self.particulas = particulas_activas
        
        # Actualizar partículas secundarias (humo)
        particulas_secundarias_activas = []
        for particula in self.particulas_secundarias:
            # El humo se mueve más lento y es afectado menos por gravedad
            particula.velocidad_y += 0.03  # Menos gravedad que las partículas de fuego
            particula.velocidad_x *= 0.98  # Fricción del aire
            particula.velocidad_y *= 0.98
            
            if particula.actualizar():
                particulas_secundarias_activas.append(particula)
                particula.dibujar(pantalla)
        self.particulas_secundarias = particulas_secundarias_activas
        
        # Verificar si todavía hay efectos activos
        self.activo = (
            len(self.particulas) > 0 or 
            len(self.particulas_secundarias) > 0 or 
            self.tiempo_explosion > 0 or 
            self.onda_expansion is not None
        )

    def crear_efecto_exito(self, x, y):
        self.particulas = []
        self.particulas_secundarias = []
        self.tiempo_explosion = 20  # Destello más corto que la explosión
        
        # Partículas de celebración (como fuegos artificiales)
        for _ in range(PARTICULAS_EXITO):
            angulo = random.uniform(-math.pi, 0)  # Solo hacia arriba
            velocidad = random.uniform(3, 8)
            velocidad_x = math.cos(angulo) * velocidad
            velocidad_y = math.sin(angulo) * velocidad
            color = random.choice(COLOR_EXITO)
            tamaño = random.randint(2, 6)
            vida = random.randint(40, 80)
            self.particulas.append(Particula(x, y, color, velocidad_x, velocidad_y, vida, tamaño))
        
        # Partículas secundarias (brillos más pequeños)
        for _ in range(PARTICULAS_EXITO // 2):
            angulo = random.uniform(-math.pi, math.pi)  # En todas direcciones
            velocidad = random.uniform(1, 3)
            velocidad_x = math.cos(angulo) * velocidad
            velocidad_y = math.sin(angulo) * velocidad
            # Usar colores más brillantes para el efecto de éxito
            color = (255, 255, 150) if random.random() > 0.5 else (150, 255, 150)
            tamaño = random.randint(1, 3)
            vida = random.randint(30, 60)
            self.particulas_secundarias.append(Particula(x, y, color, velocidad_x, velocidad_y, vida, tamaño))
        
        # Crear onda de celebración (círculos concéntricos)
        self.onda_expansion = {
            'x': x,
            'y': y,
            'radio': 5,
            'max_radio': 40,
            'vida': 30
        }
        
        self.activo = True

class Nave:
    def __init__(self, nivel=1):
        # Atributos existentes
        self.x = ANCHO // 2
        self.y = 100
        self.ancho = 40
        self.alto = 60
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.angulo = 0
        
        # Ajustar valores según el nivel
        self.nivel = nivel
        self.fuel = FUEL_POR_NIVEL.get(nivel, 400)
        self.gravedad = GRAVEDAD  # Usar la gravedad constante
        self.viento_max = VIENTO_POR_NIVEL.get(nivel, 0.02)
        
        # Nuevas propiedades
        self.sonidos = None
        self.propulsor_activo = False
        self.propulsor_izquierda = False
        self.propulsor_derecha = False
        self.modo_precision = False
        
        self.viento = 0
        self.direccion_viento = 1
        self.tiempo_cambio_viento = 0
        
        self.efectos = EfectosVisuales()
        self.particulas_propulsor = []
        
        self.aterrizado = False
        self.estrellado = False
        self.tiempo_inicio = pygame.time.get_ticks()
        self.puntuacion = 0
        self.velocidad_final = 0
        self.razon_accidente = ""
        self.desglose = {}
        
        # Historial para radar de trayectoria
        self.historial_posiciones = []
        self.ultimo_registro = 0
        self.base = None  # Añadir referencia a la base

    def actualizar(self):
        if self.aterrizado or self.estrellado:
            return
        
        if not self.aterrizado and not self.estrellado:
            # Registrar posición cada 10 frames para el radar
            if pygame.time.get_ticks() - self.ultimo_registro > 100:
                if len(self.historial_posiciones) > 20:
                    self.historial_posiciones.pop(0)
                self.historial_posiciones.append((self.x, self.y))
                self.ultimo_registro = pygame.time.get_ticks()
            
            # Actualizar viento
            if random.random() < CAMBIO_VIENTO:
                if abs(self.viento) >= self.viento_max:
                    self.direccion_viento *= -1
                self.viento += VIENTO_INCREMENTO * self.direccion_viento
            
            # Limitar el viento
            self.viento = max(-self.viento_max, min(self.viento_max, self.viento))
            
            # Aplicar gravedad
            self.velocidad_y += self.gravedad
            
            # Aplicar viento a la velocidad horizontal
            self.velocidad_x += self.viento
            
            # Controles de la nave
            if self.propulsor_activo and self.fuel > 0:
                factor_empuje = MODO_PRECISION if self.modo_precision else 1.0
                self.velocidad_y -= EMPUJE * factor_empuje
                self.fuel = max(0, self.fuel - 1 * factor_empuje)
                
                # Crear partículas del propulsor
                for _ in range(2):
                    particula = Particula(
                        self.x + self.ancho//2,
                        self.y + self.alto,
                        random.choice(COLOR_FUEGO),
                        random.uniform(-0.5, 0.5),
                        random.uniform(2, 4),
                        random.randint(20, 30),
                        random.randint(2, 4)
                    )
                    self.particulas_propulsor.append(particula)
                if self.sonidos:
                    self.sonidos.reproducir_propulsor()
            
            # Propulsores laterales
            if self.propulsor_izquierda and self.fuel > 0:
                factor_empuje = MODO_PRECISION if self.modo_precision else 1.0
                self.velocidad_x -= EMPUJE_LATERAL * factor_empuje
                self.fuel = max(0, self.fuel - 0.5 * factor_empuje)
                if self.sonidos:
                    self.sonidos.reproducir_propulsor_lateral()
            elif self.propulsor_derecha and self.fuel > 0:
                factor_empuje = MODO_PRECISION if self.modo_precision else 1.0
                self.velocidad_x += EMPUJE_LATERAL * factor_empuje
                self.fuel = max(0, self.fuel - 0.5 * factor_empuje)
                if self.sonidos:
                    self.sonidos.reproducir_propulsor_lateral()
            
            # Actualizar posición
            self.x += self.velocidad_x
            self.y += self.velocidad_y
            
            # Mantener la nave dentro de los límites horizontales
            if self.x < self.ancho / 2:
                self.x = self.ancho / 2
                self.velocidad_x = 0
            elif self.x > ANCHO - self.ancho / 2:
                self.x = ANCHO - self.ancho / 2
                self.velocidad_x = 0
            
            # Verificar aterrizaje
            altura_patas = 10
            altura_base = ALTO - SUELO_ALTURA - BASE_ALTURA_SOBRE_SUELO

            # Verificar si está sobre la base usando la posición actual de la base
            sobre_base = (self.x + self.ancho > self.base.x - self.base.ancho//2 and 
                         self.x < self.base.x + self.base.ancho//2)

            if self.y + self.alto + altura_patas >= altura_base:
                velocidad_vertical = abs(self.velocidad_y)
                velocidad_horizontal = abs(self.velocidad_x)
                
                if sobre_base:
                    # Ajustar la posición de la nave para que las patas toquen la base
                    self.y = altura_base - self.alto - altura_patas
                    
                    if velocidad_vertical <= VELOCIDAD_MAXIMA_ATERRIZAJE and velocidad_horizontal <= VELOCIDAD_MAXIMA_ATERRIZAJE / 2:
                        if not self.aterrizado:
                            self.aterrizado = True
                            self.efectos.crear_efecto_exito(self.x, self.y + self.alto)
                            if self.sonidos:
                                self.sonidos.reproducir_exito()
                            self.tiempo_espera_puntuacion = pygame.time.get_ticks() + 1500
                            self.velocidad_x = 0
                            self.velocidad_y = 0
                        else:
                            self.estrellado = True
                            self.razon_accidente = "¡Fuera de la zona de aterrizaje!"
                            if self.sonidos:
                                self.sonidos.reproducir_explosion()  # Reproducir sonido de explosión
                    else:
                        if not self.estrellado:  # Solo reproducir el sonido una vez
                            self.estrellado = True
                            if self.sonidos:
                                self.sonidos.reproducir_explosion()
                            self.razon_accidente = f"¡Velocidad excesiva! V: {velocidad_vertical:.1f} H: {velocidad_horizontal:.1f}"
                else:
                    self.estrellado = True
                    self.razon_accidente = "¡Fuera de la zona de aterrizaje!"
                    if self.sonidos:
                        self.sonidos.reproducir_explosion()  # Reproducir sonido de explosión
            
            # Luego verificar colisión con el suelo
            elif self.y + self.alto + altura_patas >= ALTO - 50:  # Verificar con la parte inferior de la nave
                self.estrellado = True
                self.velocidad_final = (self.velocidad_x ** 2 + self.velocidad_y ** 2) ** 0.5
                
                # Asignar una distancia_centro predeterminada para evitar errores
                self.distancia_centro = ANCHO  # Un valor grande (fuera de la base)
                
                # Razón del accidente
                self.razon_accidente = "¡Aterrizaje fuera de la base!"
                
                self.velocidad_x = 0
                self.velocidad_y = 0
            
            # Actualizar partículas del propulsor
            particulas_activas = []
            for particula in self.particulas_propulsor:
                if particula.actualizar():
                    particulas_activas.append(particula)
            self.particulas_propulsor = particulas_activas
        else:
            pass

    def calcular_puntuacion(self):
        if self.estrellado:
            self.puntuacion = 0
            self.desglose = {
                'base': 0,
                'velocidad': 0,
                'fuel': 0,
                'tiempo': 0,
                'precisión': 0  # Añadir esto para evitar KeyError
            }
            return  # Importante: retornar aquí para evitar ejecutar el resto
        
        # Si llegamos aquí, la nave aterrizó con éxito
        tiempo_transcurrido = (pygame.time.get_ticks() - self.tiempo_inicio) / 1000
        
        # Puntuación base
        puntos_base = 500
        
        # Bonus por velocidad
        if self.velocidad_final < 0.5:
            bonus_velocidad = 1000
        elif self.velocidad_final < 1.0:
            bonus_velocidad = 800
        elif self.velocidad_final < 1.5:
            bonus_velocidad = 500
        else:
            bonus_velocidad = 200
        
        # Bonus por combustible
        porcentaje_fuel = (self.fuel / FUEL_POR_NIVEL.get(self.nivel, 400))
        bonus_fuel = int(1000 * (porcentaje_fuel ** 2))
        
        # Bonus por tiempo
        if tiempo_transcurrido < 20:
            bonus_tiempo = 500
        elif tiempo_transcurrido < 30:
            bonus_tiempo = 300
        elif tiempo_transcurrido < 40:
            bonus_tiempo = 100
        else:
            bonus_tiempo = max(0, int(500 - (tiempo_transcurrido - 20) * 10))
        
        # Bonus por precisión (con verificación adicional)
        try:
            if hasattr(self, 'distancia_centro'):
                precision = 1 - min(1.0, (self.distancia_centro / (BASE_ANCHO//2)))
                bonus_precision = int(1000 * (precision ** 2))
            else:
                # Si no tenemos información de distancia, asumimos precisión media
                bonus_precision = 500
        except:
            # En caso de cualquier error, asignar un valor seguro
            bonus_precision = 500
        
        self.puntuacion = puntos_base + bonus_velocidad + bonus_fuel + bonus_tiempo + bonus_precision
        
        self.desglose = {
            'base': puntos_base,
            'velocidad': bonus_velocidad,
            'fuel': bonus_fuel,
            'tiempo': bonus_tiempo,
            'precisión': bonus_precision
        }

    def dibujar(self):
        # Dibujar cuerpo principal de la nave
        puntos_nave = [
            (self.x - self.ancho//2, self.y + self.alto),  # Base izquierda
            (self.x + self.ancho//2, self.y + self.alto),  # Base derecha
            (self.x + self.ancho//3, self.y + self.alto//3),  # Lateral derecho
            (self.x, self.y),  # Punta
            (self.x - self.ancho//3, self.y + self.alto//3),  # Lateral izquierdo
        ]
        pygame.draw.polygon(pantalla, COLOR_BLANCO, puntos_nave)
        pygame.draw.polygon(pantalla, COLOR_GRIS, puntos_nave, 2)  # Borde
        
        # Dibujar ventana de la nave
        centro_ventana = (self.x, self.y + self.alto//3)
        radio_ventana = self.ancho//4
        pygame.draw.circle(pantalla, COLOR_AZUL, centro_ventana, radio_ventana)
        pygame.draw.circle(pantalla, COLOR_BLANCO, centro_ventana, radio_ventana, 1)
        
        # Dibujar patas de aterrizaje
        pata_izq = [(self.x - self.ancho//2, self.y + self.alto),
                    (self.x - self.ancho//2 - 5, self.y + self.alto + 10)]
        pata_der = [(self.x + self.ancho//2, self.y + self.alto),
                    (self.x + self.ancho//2 + 5, self.y + self.alto + 10)]
        pygame.draw.lines(pantalla, COLOR_BLANCO, False, pata_izq, 2)
        pygame.draw.lines(pantalla, COLOR_BLANCO, False, pata_der, 2)
        
        if self.fuel > 0:
            # Dibujar propulsor principal con efecto de fuego
            if self.propulsor_activo:
                for i, color in enumerate(COLOR_FUEGO):
                    tamaño = 10 - i * 2
                    offset = i * 3
                    puntos_fuego = [
                        (self.x - tamaño//2, self.y + self.alto + offset),
                        (self.x + tamaño//2, self.y + self.alto + offset),
                        (self.x, self.y + self.alto + tamaño + offset)
                    ]
                    pygame.draw.polygon(pantalla, color, puntos_fuego)
            
            # Dibujar propulsores laterales con efecto de fuego
            if self.propulsor_izquierda:
                for i, color in enumerate(COLOR_FUEGO):
                    tamaño = 8 - i * 2
                    offset = i * 2
                    puntos_fuego = [
                        (self.x + self.ancho//2 + offset, self.y + self.alto//3),
                        (self.x + self.ancho//2 + offset, self.y + self.alto//3 + tamaño),
                        (self.x + self.ancho//2 + tamaño + offset, self.y + self.alto//3 + tamaño//2)
                    ]
                    pygame.draw.polygon(pantalla, color, puntos_fuego)
            
            if self.propulsor_derecha:
                for i, color in enumerate(COLOR_FUEGO):
                    tamaño = 8 - i * 2
                    offset = i * 2
                    puntos_fuego = [
                        (self.x - self.ancho//2 - offset, self.y + self.alto//3),
                        (self.x - self.ancho//2 - offset, self.y + self.alto//3 + tamaño),
                        (self.x - self.ancho//2 - tamaño - offset, self.y + self.alto//3 + tamaño//2)
                    ]
                    pygame.draw.polygon(pantalla, color, puntos_fuego)

class SistemaPuntuacion:
    def __init__(self):
        self.nivel_actual = 1
        self.desbloqueos = {
            1000: "control_horizontal",
            2000: "escudo",
            3000: "propulsor_mejorado"
        }
    
    def verificar_desbloqueos(self, puntuacion):
        for puntos, mejora in self.desbloqueos.items():
            if puntuacion >= puntos:
                return mejora

def dibujar_suelo():
    pygame.draw.rect(pantalla, COLOR_BLANCO, (0, ALTO - 50, ANCHO, 50))

def dibujar_hud(nave):
    fuente = pygame.font.Font(None, 36)
    
    # Color basado en la velocidad (rojo si es peligrosa)
    color_vel_y = COLOR_ROJO if abs(nave.velocidad_y) > VELOCIDAD_MAXIMA_ATERRIZAJE else COLOR_BLANCO
    color_vel_x = COLOR_ROJO if abs(nave.velocidad_x) > VELOCIDAD_MAXIMA_ATERRIZAJE/2 else COLOR_BLANCO
    
    texto_vel_y = fuente.render(f"Velocidad V: {abs(nave.velocidad_y):.1f}", True, color_vel_y)
    texto_vel_x = fuente.render(f"Velocidad H: {abs(nave.velocidad_x):.1f}", True, color_vel_x)
    
    # Color para combustible basado en la cantidad restante
    fuel_ratio = nave.fuel / FUEL_POR_NIVEL[nave.nivel]
    if fuel_ratio > 0.5:
        color_fuel = COLOR_VERDE
    elif fuel_ratio > 0.25:
        color_fuel = COLOR_AMARILLO
    else:
        color_fuel = COLOR_ROJO
    
    texto_fuel = fuente.render(f"Fuel: {nave.fuel}", True, color_fuel)
    
    # Texto para el viento
    if abs(nave.viento) < 0.005:
        texto_viento = fuente.render(f"Viento: {nave.viento:.3f} (Calma)", True, COLOR_BLANCO)
    else:
        direccion = " ←" if nave.viento < 0 else " →"
        intensidad = abs(nave.viento) / nave.viento_max
        if intensidad > 0.7:
            texto_intensidad = "Fuerte" 
            color_viento = COLOR_ROJO
        elif intensidad > 0.3:
            texto_intensidad = "Moderado"
            color_viento = COLOR_AMARILLO
        else:
            texto_intensidad = "Suave"
            color_viento = COLOR_BLANCO
        
        texto_viento = fuente.render(f"Viento: {abs(nave.viento):.3f} {texto_intensidad}{direccion}", True, color_viento)
    
    # Modo precisión
    if nave.modo_precision:
        texto_precision = fuente.render("MODO PRECISIÓN", True, COLOR_VERDE)
        pantalla.blit(texto_precision, (ANCHO - 200, 10))
    
    # Nivel actual
    texto_nivel = fuente.render(f"Nivel: {nave.nivel}", True, COLOR_AMARILLO)
    pantalla.blit(texto_nivel, (ANCHO - 150, 50))
    
    pantalla.blit(texto_vel_y, (10, 10))
    pantalla.blit(texto_vel_x, (10, 50))
    pantalla.blit(texto_fuel, (10, 90))
    pantalla.blit(texto_viento, (10, 130))
    
    # Mostrar radar de trayectoria
    if len(nave.historial_posiciones) > 1:
        for i in range(1, len(nave.historial_posiciones)):
            pos_ant = nave.historial_posiciones[i-1]
            pos_act = nave.historial_posiciones[i]
            # Color que se desvanece con el tiempo
            alpha = int(255 * (i / len(nave.historial_posiciones)))
            pygame.draw.line(pantalla, (100, 100, 255, alpha), pos_ant, pos_act, 1)
    
    # Dibujar indicador de zona segura si está activado
    if INDICADOR_ATERRIZAJE and not nave.aterrizado and not nave.estrellado:
        # Usar la posición actual de la base
        pygame.draw.rect(pantalla, COLOR_VERDE,
                        (nave.base.x - BASE_ANCHO//2, ALTO - SUELO_ALTURA - BASE_ALTURA_SOBRE_SUELO - 5,
                         BASE_ANCHO, 5), 1)

def mostrar_pantalla_inicio():
    pantalla.fill((0, 0, 0))  # Fondo negro
    fuente_grande = pygame.font.Font(None, 74)
    fuente_pequeña = pygame.font.Font(None, 36)
    
    # Título
    titulo = fuente_grande.render("ATERRIZAJE LUNAR", True, COLOR_BLANCO)
    rect_titulo = titulo.get_rect(center=(ANCHO//2, ALTO//3))
    
    # Instrucciones
    instrucciones = [
        "Presiona ESPACIO para usar el propulsor",
        "← y → para mover lateralmente",
        "¡Cuidado con el viento!"
    ]
    
    for i, texto in enumerate(instrucciones):
        instr = fuente_pequeña.render(texto, True, COLOR_BLANCO)
        rect_instr = instr.get_rect(center=(ANCHO//2, ALTO//2 + i*30))
        pantalla.blit(instr, rect_instr)
    
    mensaje = fuente_pequeña.render("Presiona ENTER para comenzar", True, COLOR_VERDE)
    rect_mensaje = mensaje.get_rect(center=(ANCHO//2, ALTO*2//3 + 30))
    
    pantalla.blit(titulo, rect_titulo)
    pantalla.blit(mensaje, rect_mensaje)
    pygame.display.flip()

def mostrar_tabla_records(tablero):
    pantalla.fill((0, 0, 0))
    fuente_grande = pygame.font.Font(None, 74)
    fuente_pequeña = pygame.font.Font(None, 36)
    
    # Título
    titulo = fuente_grande.render("TOP 10 PUNTUACIONES", True, COLOR_AMARILLO)
    rect_titulo = titulo.get_rect(center=(ANCHO//2, 50))
    pantalla.blit(titulo, rect_titulo)
    
    # Mostrar puntuaciones
    y_pos = 150
    for i, record in enumerate(tablero.obtener_top_10(), 1):
        texto = f"{i}. {record['puntuacion']} pts - {record['fecha']}"
        linea = fuente_pequeña.render(texto, True, COLOR_BLANCO)
        rect_linea = linea.get_rect(center=(ANCHO//2, y_pos))
        pantalla.blit(linea, rect_linea)
        y_pos += 40
    
    # Mensaje para continuar
    mensaje = fuente_pequeña.render("Presiona ESPACIO para continuar", True, COLOR_VERDE)
    rect_mensaje = mensaje.get_rect(center=(ANCHO//2, ALTO - 50))
    pantalla.blit(mensaje, rect_mensaje)
    
    pygame.display.flip()

def mostrar_seleccion_nivel(sonidos):
    pantalla.fill((0, 0, 0))
    fuente_grande = pygame.font.Font(None, 60)
    fuente_mediana = pygame.font.Font(None, 48)
    fuente_pequeña = pygame.font.Font(None, 36)
    
    titulo = fuente_grande.render("SELECCIÓN DE NIVEL", True, COLOR_AMARILLO)
    rect_titulo = titulo.get_rect(center=(ANCHO//2, 80))
    pantalla.blit(titulo, rect_titulo)
    
    for nivel in range(1, 4):
        # Determinar color según dificultad
        if nivel == 1:
            color = COLOR_VERDE
            dificultad = "Fácil"
        elif nivel == 2:
            color = COLOR_AMARILLO
            dificultad = "Medio"
        else:
            color = COLOR_ROJO
            dificultad = "Difícil"
            
        # Texto del nivel
        y_pos = 150 + nivel * 70
        texto_nivel = fuente_mediana.render(f"Nivel {nivel}: {dificultad}", True, color)
        rect_nivel = texto_nivel.get_rect(center=(ANCHO//2, y_pos))
        pantalla.blit(texto_nivel, rect_nivel)
        
        # Detalles del nivel (sin mostrar la gravedad ya que es constante)
        texto_detalles = fuente_pequeña.render(
            f"Fuel: {FUEL_POR_NIVEL[nivel]} | Viento máx: {VIENTO_POR_NIVEL[nivel]}",
            True, COLOR_BLANCO
        )
        rect_detalles = texto_detalles.get_rect(center=(ANCHO//2, y_pos + 30))
        pantalla.blit(texto_detalles, rect_detalles)
    
    instrucciones = fuente_pequeña.render("Selecciona un nivel (1-3)", True, COLOR_BLANCO)
    rect_instr = instrucciones.get_rect(center=(ANCHO//2, ALTO - 50))
    pantalla.blit(instrucciones, rect_instr)
    
    pygame.display.flip()
    
    nivel_seleccionado = 1
    seleccionando = True
    while seleccionando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    nivel_seleccionado = int(pygame.key.name(evento.key))
                    sonidos.reproducir_inicio()  # Reproducir sonido al seleccionar nivel
                    seleccionando = False
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    
    return nivel_seleccionado

def main():
    sonidos = Sonidos()
    tablero_records = TableroRecords()
    estrellas = Estrellas()
    
    while True:
        # Pantalla de inicio
        mostrar_pantalla_inicio()
        esperando_inicio = True
        while esperando_inicio:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    sonidos.detener_todos()
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN:
                        esperando_inicio = False
                        sonidos.reproducir_inicio()
                    elif evento.key == pygame.K_ESCAPE:
                        sonidos.detener_todos()
                        pygame.quit()
                        sys.exit()
        
        # Selección de nivel
        nivel = mostrar_seleccion_nivel(sonidos)
        
        # Iniciar nueva partida
        base = Base(nivel)  # Crear base primero
        nave = Nave(nivel)
        nave.sonidos = sonidos
        nave.base = base  # Asignar la base a la nave
        jugando = True
        aterrizado_anterior = False
        estrellado_anterior = False
        
        while jugando:
            tiempo_actual = pygame.time.get_ticks()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    sonidos.detener_todos()
                    pygame.quit()
                    sys.exit()
                
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        nave.propulsor_activo = True
                    elif evento.key == pygame.K_LEFT:
                        nave.propulsor_izquierda = True
                    elif evento.key == pygame.K_RIGHT:
                        nave.propulsor_derecha = True
                    elif evento.key == pygame.K_LSHIFT or evento.key == pygame.K_RSHIFT:
                        nave.modo_precision = True
                        sonidos.reproducir_precision()
                    elif evento.key == pygame.K_ESCAPE:
                        sonidos.detener_todos()
                        pygame.quit()
                        sys.exit()
                
                if evento.type == pygame.KEYUP:
                    if evento.key == pygame.K_SPACE:
                        nave.propulsor_activo = False
                    elif evento.key == pygame.K_LEFT:
                        nave.propulsor_izquierda = False
                    elif evento.key == pygame.K_RIGHT:
                        nave.propulsor_derecha = False
                    elif evento.key == pygame.K_LSHIFT or evento.key == pygame.K_RSHIFT:
                        nave.modo_precision = False

            # Actualizar sonidos basado en el estado de los propulsores
            if nave.propulsor_activo and nave.fuel > 0:
                sonidos.reproducir_propulsor()
            if (nave.propulsor_izquierda or nave.propulsor_derecha) and nave.fuel > 0:
                sonidos.reproducir_propulsor_lateral()
            
            # Actualizar
            nave.actualizar()
            
            # Verificar si acaba de aterrizar o estrellarse
            if nave.aterrizado and not aterrizado_anterior:
                sonidos.reproducir_exito()
                aterrizado_anterior = True
            elif nave.estrellado and not estrellado_anterior:
                sonidos.reproducir_explosion()
                estrellado_anterior = True
            
            # Dibujar
            pantalla.fill((0, 0, 0))
            estrellas.dibujar()  # Dibujar estrellas antes que todo
            dibujar_suelo()
            base.dibujar(nave.viento)
            nave.dibujar()
            nave.efectos.actualizar_y_dibujar(pantalla)  # Dibujar efectos
            dibujar_hud(nave)

            # Si ha terminado la partida
            if nave.aterrizado or nave.estrellado:
                # Si es un aterrizaje, esperar el tiempo necesario para que se escuche el sonido
                if nave.aterrizado and hasattr(nave, 'tiempo_espera_puntuacion'):
                    tiempo_actual = pygame.time.get_ticks()
                    if tiempo_actual < nave.tiempo_espera_puntuacion:
                        # Seguir actualizando la pantalla mientras esperamos
                        pygame.display.flip()
                        reloj.tick(FPS)
                        continue  # Continuar el bucle sin mostrar pantalla de puntuación
                
                # Ahora sí calcular puntuación y mostrar resultados
                nave.calcular_puntuacion()
                
                # Determinar si la puntuación está en el top 10 y en qué posición
                es_top10 = False
                posicion_top = 0
                
                if nave.aterrizado:
                    # Comprobar posición en el top 10
                    puntuaciones_actuales = tablero_records.obtener_top_10()
                    for i, record in enumerate(puntuaciones_actuales, 1):
                        if nave.puntuacion > record['puntuacion']:
                            posicion_top = i
                            es_top10 = True
                            break
                    
                    # Si no encontramos posición pero hay menos de 10 records
                    if not es_top10 and len(puntuaciones_actuales) < 10:
                        posicion_top = len(puntuaciones_actuales) + 1
                        es_top10 = True
                    
                    # Guardar puntuación
                    fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                    tablero_records.agregar_puntuacion({
                        'puntuacion': nave.puntuacion,
                        'fecha': fecha
                    })
                
                fuente_grande = pygame.font.Font(None, 84)
                fuente_normal = pygame.font.Font(None, 48)
                fuente_pequeña = pygame.font.Font(None, 36)
                
                # Crear superficie semitransparente para el fondo
                overlay = pygame.Surface((ANCHO, ALTO))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(160)  # Un poco más oscuro para mejor contraste
                pantalla.blit(overlay, (0, 0))
                
                # Mensaje principal y puntuación
                if nave.aterrizado:
                    mensaje = "¡ATERRIZAJE EXITOSO!"
                    mensaje_puntos = f"Puntuación Total: {nave.puntuacion}"
                    color_mensaje = COLOR_VERDE
                else:
                    mensaje = "¡ESTRELLADO!"
                    mensaje_puntos = "Puntuación: 0"
                    color_mensaje = COLOR_ROJO
                
                # Dibujar mensaje principal
                texto = fuente_grande.render(mensaje, True, color_mensaje)
                rect_texto = texto.get_rect(center=(ANCHO//2, ALTO//5))  # Más arriba
                pantalla.blit(texto, rect_texto)
                
                # Dibujar puntuación total
                texto_puntos = fuente_normal.render(mensaje_puntos, True, COLOR_AMARILLO)
                rect_puntos = texto_puntos.get_rect(center=(ANCHO//2, ALTO//5 + 70))  # Ajustado
                pantalla.blit(texto_puntos, rect_puntos)
                
                # Mostrar mensaje si entró al top 10
                if es_top10:
                    mensaje_top = fuente_normal.render(f"¡TOP 10! - Posición #{posicion_top}", True, COLOR_VERDE)
                    rect_top = mensaje_top.get_rect(center=(ANCHO//2, ALTO//5 + 140))  # Más separado
                    pantalla.blit(mensaje_top, rect_top)
                
                # Columna izquierda: Desglose de puntuación o mensaje de error
                if nave.aterrizado:
                    x_desglose = ANCHO//4 - 50
                    y_desglose = ALTO//2
                    
                    titulo_desglose = fuente_pequeña.render("DESGLOSE", True, COLOR_AMARILLO)
                    rect_titulo = titulo_desglose.get_rect(center=(x_desglose, y_desglose))
                    pantalla.blit(titulo_desglose, rect_titulo)
                    
                    for i, (concepto, puntos) in enumerate(nave.desglose.items()):
                        texto = f"{concepto.capitalize()}: {puntos}"
                        linea = fuente_pequeña.render(texto, True, COLOR_BLANCO)
                        rect_linea = linea.get_rect(center=(x_desglose, y_desglose + 40 + i * 35))
                        pantalla.blit(linea, rect_linea)
                else:
                    # Mejor posicionamiento para el mensaje de accidente
                    y_razon = ALTO//5 + 180  # Más espacio debajo del mensaje principal
                    
                    # Dividir razón de accidente en dos líneas si es necesario
                    if len(nave.razon_accidente) > 30:
                        mitad = nave.razon_accidente.find(" ", len(nave.razon_accidente)//2)
                        if mitad == -1:  # Si no hay espacios, dividir en mitad
                            mitad = len(nave.razon_accidente)//2
                        
                        texto_razon1 = fuente_normal.render(nave.razon_accidente[:mitad], True, COLOR_ROJO)
                        texto_razon2 = fuente_normal.render(nave.razon_accidente[mitad:], True, COLOR_ROJO)
                        
                        rect_razon1 = texto_razon1.get_rect(center=(ANCHO//2, y_razon))
                        rect_razon2 = texto_razon2.get_rect(center=(ANCHO//2, y_razon + 50))
                        
                        pantalla.blit(texto_razon1, rect_razon1)
                        pantalla.blit(texto_razon2, rect_razon2)
                    else:
                        texto_razon = fuente_normal.render(nave.razon_accidente, True, COLOR_ROJO)
                        rect_razon = texto_razon.get_rect(center=(ANCHO//2, y_razon))
                        pantalla.blit(texto_razon, rect_razon)
                    
                    # Información adicional sobre el accidente
                    if hasattr(nave, 'velocidad_final'):
                        y_info = y_razon + (100 if len(nave.razon_accidente) > 30 else 60)
                        
                        vel_total = fuente_pequeña.render(f"Velocidad final: {nave.velocidad_final:.1f}", True, COLOR_BLANCO)
                        vel_vert = fuente_pequeña.render(f"Velocidad vertical: {abs(nave.velocidad_y):.1f}", True, COLOR_BLANCO)
                        vel_horiz = fuente_pequeña.render(f"Velocidad horizontal: {abs(nave.velocidad_x):.1f}", True, COLOR_BLANCO)
                        
                        pantalla.blit(vel_total, vel_total.get_rect(center=(ANCHO//2, y_info)))
                        pantalla.blit(vel_vert, vel_vert.get_rect(center=(ANCHO//2, y_info + 35)))
                        pantalla.blit(vel_horiz, vel_horiz.get_rect(center=(ANCHO//2, y_info + 70)))
                
                # Columna derecha: TOP 10 (solo en caso de aterrizaje exitoso)
                if nave.aterrizado:
                    x_records = ANCHO * 3//4 + 50  # Más a la derecha
                    y_records = ALTO//2
                    
                    titulo_top = fuente_pequeña.render("MEJORES PUNTUACIONES", True, COLOR_AMARILLO)
                    rect_top = titulo_top.get_rect(center=(x_records, y_records))
                    pantalla.blit(titulo_top, rect_top)
                    
                    # Limitamos a mostrar solo 8 puntuaciones para evitar sobreposiciones
                    for i, record in enumerate(tablero_records.obtener_top_10()[:8], 1):
                        texto = f"{i}. {record['puntuacion']} pts"
                        
                        # Destacar la nueva puntuación
                        if es_top10 and i == posicion_top:
                            color = COLOR_VERDE
                            texto += " ← ¡NUEVO!"
                        else:
                            color = COLOR_AMARILLO if i == 1 else COLOR_BLANCO
                            
                        linea = fuente_pequeña.render(texto, True, color)
                        rect_linea = linea.get_rect(center=(x_records, y_records + 40 + i * 30))
                        pantalla.blit(linea, rect_linea)
                
                # Mensaje para continuar en la parte inferior
                mensaje_continuar = fuente_pequeña.render("Presiona ESPACIO para continuar", True, COLOR_VERDE)
                rect_continuar = mensaje_continuar.get_rect(center=(ANCHO//2, ALTO - 40))
                pantalla.blit(mensaje_continuar, rect_continuar)
                
                pygame.display.flip()
                
                # Esperar input para continuar
                esperando_continuar = True
                while esperando_continuar:
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_SPACE:
                                esperando_continuar = False
                                jugando = False
                            elif evento.key == pygame.K_ESCAPE:
                                pygame.quit()
                                sys.exit()
            
            # Actualizar pantalla si el juego sigue en curso
            else:
                pygame.display.flip()
                reloj.tick(FPS)

if __name__ == "__main__":
    main()
