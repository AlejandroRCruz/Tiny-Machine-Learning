from pydub import AudioSegment
import os

# ===============================
# 1. Convertir M4A → WAV
# ===============================

entrada = "Grabación.m4a"     # Cambia por tu archivo
salida_wav = "salida.wav"

audio = AudioSegment.from_file(entrada, format="m4a")
audio.export(salida_wav, format="wav")
print("Archivo convertido a WAV:", salida_wav)

# ===============================
# 2. Partir WAV en segmentos de 1 segundo
# ===============================

segmentos_dir = "segmentos"
os.makedirs(segmentos_dir, exist_ok=True)

duracion_ms = len(audio)  # duración total en milisegundos
segmento_ms = 1000        # 1 s

for i in range(0, duracion_ms, segmento_ms):
    segmento = audio[i:i+segmento_ms]
    nombre_seg = os.path.join(segmentos_dir, f"seg_{i//1000:04d}.wav")
    segmento.export(nombre_seg, format="wav")

print("Segmentación completa. Archivos guardados en:", segmentos_dir)
