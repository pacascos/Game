import json
import os

class TableroRecords:
    def __init__(self):
        self.archivo = "high_scores.json"
        self.puntuaciones = []
        self.cargar_puntuaciones()

    def cargar_puntuaciones(self):
        try:
            if os.path.exists(self.archivo):
                with open(self.archivo, 'r') as f:
                    self.puntuaciones = json.load(f)
        except:
            self.puntuaciones = []

    def guardar_puntuaciones(self):
        with open(self.archivo, 'w') as f:
            json.dump(self.puntuaciones, f)

    def agregar_puntuacion(self, puntuacion):
        self.puntuaciones.append(puntuacion)
        self.puntuaciones.sort(key=lambda x: x['puntuacion'], reverse=True)
        self.puntuaciones = self.puntuaciones[:10]  # Mantener solo los 10 mejores
        self.guardar_puntuaciones()

    def obtener_top_10(self):
        return self.puntuaciones[:10] 