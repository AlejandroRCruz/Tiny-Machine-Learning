from pydub import AudioSegment
import os, glob, random, array

# ===========================================================
# EFECTOS
# ===========================================================

def filtro_pasabaja(audio):
    cutoff = random.randint(1000, 6000)
    return audio.low_pass_filter(cutoff)

def filtro_pasalta(audio):
    cutoff = random.randint(100, 2000)
    return audio.high_pass_filter(cutoff)

def ruido_blanco(audio):
    intensidad = random.randint(-35, -10)
    ruido = AudioSegment(
        data=bytes([random.randint(0, 255) for _ in range(len(audio.raw_data))]),
        sample_width=audio.sample_width,
        frame_rate=audio.frame_rate,
        channels=audio.channels
    )
    ruido = ruido - abs(intensidad)
    return audio.overlay(ruido)

def ruido_rosa(audio):
    intensidad = random.randint(-35, -15)
    ruido = ruido_blanco(audio)
    ruido = ruido.low_pass_filter(random.randint(500,1500))
    return audio.overlay(ruido)

def ruido_estatico(audio):
    intensidad = random.randint(-30, -15)
    muestras = bytearray(audio.raw_data)
    for i in range(0, len(muestras), random.randint(200, 600)):
        muestras[i] = random.randint(0, 255)
    ruido = AudioSegment(
        data=bytes(muestras),
        sample_width=audio.sample_width,
        frame_rate=audio.frame_rate,
        channels=audio.channels
    )
    ruido = ruido - abs(intensidad)
    return audio.overlay(ruido)

def eco(audio):
    retraso = random.randint(80, 300)
    atenuacion = -random.randint(3, 12)
    retraso_seg = AudioSegment.silent(duration=retraso)
    eco_audio = audio + atenuacion
    return audio.overlay(retraso_seg + eco_audio)

def distorsion(audio):
    gain = random.randint(5, 25)
    audio = audio + gain
    muestras = audio.get_array_of_samples()
    tipo = muestras.typecode
    muestras = array.array(tipo, muestras)

    max_val = (2 ** (8 * audio.sample_width - 1)) - 1
    min_val = -max_val - 1

    for i in range(len(muestras)):
        if muestras[i] > max_val:
            muestras[i] = max_val
        elif muestras[i] < min_val:
            muestras[i] = min_val

    return audio._spawn(muestras.tobytes())

def pitch_shift(audio):
    semitonos = random.uniform(-4, 4)
    new_rate = int(audio.frame_rate * (2.0 ** (semitonos / 12)))
    shifted = audio._spawn(audio.raw_data, overrides={'frame_rate': new_rate})
    return shifted.set_frame_rate(audio.frame_rate)

def speed_change(audio):
    factor = random.uniform(0.75, 1.3)
    new_rate = int(audio.frame_rate * factor)
    sped = audio._spawn(audio.raw_data, overrides={'frame_rate': new_rate})
    return sped.set_frame_rate(audio.frame_rate)

# Lista de efectos disponibles (sin parámetros aquí)
EFFECTS = [
    filtro_pasabaja,
    filtro_pasalta,
    ruido_blanco,
    ruido_rosa,
    ruido_estatico,
    eco,
    distorsion,
    pitch_shift,
    speed_change
]

# ===========================================================
# PIPELINE
# ===========================================================

carpeta_entrada = "segmentos_voz"
carpeta_salida = "salida_augmentada"
os.makedirs(carpeta_salida, exist_ok=True)

lista_wavs = glob.glob(os.path.join(carpeta_entrada, "*.wav"))
print("Audios encontrados:", lista_wavs)

for wav_path in lista_wavs:
    base = os.path.splitext(os.path.basename(wav_path))[0]
    print(f"\nProcesando: {base}")

    original = AudioSegment.from_wav(wav_path)

    for i in range(100):  # GENERAR 100 VARIANTES POR AUDIO
        # Elegir cuántos efectos aplicar (1 a 4)
        k = random.randint(1, 4)

        # Elegir efectos únicos
        efectos = random.sample(EFFECTS, k)

        # Aplicar en orden aleatorio
        random.shuffle(efectos)

        mod = original
        for efecto in efectos:
            mod = efecto(mod)  # aplicar efecto

        # Guardar audio modificado
        nombre = f"{base}_aug_{i:03d}.wav"
        salida = os.path.join(carpeta_salida, nombre)
        mod.export(salida, format="wav")

        print(f"   Guardado -> {nombre}")

print("\nCOMPLETADO: 100 augmentaciones por cada WAV.")
