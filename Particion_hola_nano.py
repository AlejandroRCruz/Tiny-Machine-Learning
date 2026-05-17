from pydub import AudioSegment
import os
import glob

carpeta_entrada = "hola_nano"       # carpeta con tus WAV
carpeta_salida = "segmentos_voz"
os.makedirs(carpeta_salida, exist_ok=True)

FRAME_MS = 100
SECOND_MS = 1000
UMBRAL_DBFS = -35

# Obtener lista de .wav en la carpeta
lista_wavs = glob.glob(os.path.join(carpeta_entrada, "*.wav"))

print("Archivos encontrados:", lista_wavs)

for wav_path in lista_wavs:
    print("\nProcesando:", wav_path)

    audio = AudioSegment.from_wav(wav_path)

    segmento_actual = AudioSegment.silent(duration=0)
    voz_acumulada = 0
    indice = 0

    # Nombre base del archivo sin extensión
    nombre_base = os.path.splitext(os.path.basename(wav_path))[0]

    for i in range(0, len(audio), FRAME_MS):
        frame = audio[i:i+FRAME_MS]

        if frame.dBFS > UMBRAL_DBFS:
            segmento_actual += frame
            voz_acumulada += FRAME_MS

            # Guardar segmento de 1s
            if voz_acumulada >= SECOND_MS:
                nombre = f"{nombre_base}_{indice:04d}.wav"
                salida = os.path.join(carpeta_salida, nombre)
                segmento_actual.export(salida, format="wav")

                print("   Guardado:", salida)

                indice += 1
                voz_acumulada = 0
                segmento_actual = AudioSegment.silent(duration=0)
        else:
            # Reiniciar si hay silencio
            segmento_actual = AudioSegment.silent(duration=0)
            voz_acumulada = 0

    print(f"Terminado {indice} segmentos para {nombre_base}")

print("\nListo. Segmentación global completada.")
