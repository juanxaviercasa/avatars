import os, sys, json, subprocess, time
from pathlib import Path
from faster_whisper import WhisperModel

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
OUTPUTS_DIR = Path("outputs/quimica_piloto_10")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS = [
    (91, "Ciclo_Destructivo_CFCs_Capa_Ozono", "ciclo_destructivo_de_los_CFCs"),
    (92, "Mecanismo_Oculto_Lluvia_Acida", "mecanismo_oculto_de_la_lluvia_ácida"),
    (93, "Predecir_Cargas_Ionicas_Al_Instante", "predecir_cargas_iónicas_al_instante"),
    (94, "Calcular_Sin_Calculadora_Quimica", "calcular_sin_calculadora_en_química"),
    (95, "Detectar_Trampa_Reactivo_Limitante_Repaso", "detectar_la_trampa_del_reactivo_limitante"),
    (96, "Cuatro_Pilares_Quimica_Examen_Admision", "Los_4_pilares_de_Química"),
]

print("Cargando modelo Faster-Whisper...")
model = WhisperModel("small", device="cpu", compute_type="int8")

all_files = list(SRC_DIR.glob("*.mp4"))
manifest = {}

for num, slug, pattern in REELS_SPECS:
    matches = [f for f in all_files if pattern.lower() in f.name.lower()]
    if not matches:
        print(f"ERROR: No se encontró archivo para Reel {num} con patrón '{pattern}'")
        continue
    src_file = matches[0]
    filename = src_file.name

    workdir = OUTPUTS_DIR / f"reel_{num:02d}_zenit_pipeline"
    workdir.mkdir(parents=True, exist_ok=True)
    words_file = workdir / "04_words.json"

    # Extraer audio
    wav_path = workdir / "source_audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src_file), "-vn", "-ar", "16000", "-ac", "1", str(wav_path)], check=True)

    print(f"\n--- Transcribiendo Reel {num:02d}: {filename} ---")
    t0 = time.time()
    segments, info = model.transcribe(str(wav_path), word_timestamps=True, language="es")
    
    words_list = []
    full_text = []
    last_word_end = 0.0

    for seg in segments:
        for w in seg.words:
            w_text = w.word.strip()
            if not w_text:
                continue
            words_list.append({
                "start": round(w.start, 2),
                "end": round(w.end, 2),
                "text": w_text
            })
            if w.end > last_word_end:
                last_word_end = w.end
        full_text.append(seg.text.strip())

    with open(words_file, "w", encoding="utf-8") as f:
        json.dump(words_list, f, indent=1, ensure_ascii=False)

    text_concat = " ".join(full_text)
    end_trim = round(last_word_end + 0.35, 2)
    dt = round(time.time() - t0, 2)

    print(f"Reel {num:02d} completado en {dt}s. Palabras: {len(words_list)}. Última palabra en: {last_word_end:.2f}s -> end_trim: {end_trim:.2f}s")
    print(f"Texto inicial: {text_concat[:120]}...")
    print(f"Texto final: ...{text_concat[-120:]}")

    manifest[num] = {
        "slug": slug,
        "filename": filename,
        "total_words": len(words_list),
        "last_word_end": round(last_word_end, 2),
        "end_trim": end_trim,
        "text": text_concat
    }

manifest_path = OUTPUTS_DIR / "batch_91_to_96_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\nManifest guardado en {manifest_path}")
