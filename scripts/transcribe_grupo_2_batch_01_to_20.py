import os, sys, json, subprocess, time
from pathlib import Path
from faster_whisper import WhisperModel

# Asegurar flush de logs en tiempo real
sys.stdout.reconfigure(line_buffering=True)

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
OUTPUTS_DIR = Path("outputs/quimica_grupo_2")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_SPECS = [
    (1, "Como_Ven_Los_Quimicos_El_Mundo", "Cómo_ven_los_químicos_el_mundo.mp4"),
    (2, "Ley_vs_Teoria_Mito_Cientifico", "Ley_vs_Teoría__El_Mito_Científico.mp4"),
    (3, "Luz_Antigua_Prueba_Big_Bang", "Cómo_la_luz_antigua_prueba_el_Big_Bang.mp4"),
    (4, "Como_Dalton_Demostro_El_Atomo", "Cómo_Dalton_Demostró_el_Átomo.mp4"),
    (5, "Secreto_Tres_Estados_Materia", "El_secreto_de_los_3_estados_de_la_materia.mp4"),
    (6, "Distinguir_Propiedades_Fisicas_Quimicas", "Cómo_distinguir_propiedades_físicas_y_químicas.mp4"),
    (7, "Truco_Propiedades_Intensivas_Extensivas", "El_Truco_para_Propiedades_Intensivas_y_Extensivas.mp4"),
    (8, "Diferenciar_Compuesto_De_Mezcla", "Cómo_Diferenciar_Un_Compuesto_De_Una_Mezcla.mp4"),
    (9, "Mezclas_Homogeneas_Metodos_Separacion", "Mezclas_Homogéneas__Cómo_Separar_Lo_Que_No_Ves.mp4"),
    (10, "Dominar_Conversiones_Sistema_Internacional", "Cómo_dominar_las_conversiones_del_SI.mp4"),
    (11, "Masa_vs_Peso_Gravedad_Luna", "Por_qué_tu_peso_cambia_en_la_Luna.mp4"),
    (12, "Secreto_Geometrico_Un_Litro", "El_Secreto_Geométrico_de_un_Litro.mp4"),
    (13, "Atajo_Calcular_Convertir_Densidad", "El_Atajo_para_Calcular_y_Convertir_la_Densidad.mp4"),
    (14, "Cientificos_Escala_Kelvin_Cero_Absoluto", "Por_qué_los_científicos_usan_la_escala_Kelvin.mp4"),
    (15, "Notacion_Cientifica_Sin_Perder_Signo", "Dominando_la_notación_científica_sin_perder_el_signo.mp4"),
    (16, "Operaciones_Basicas_Notacion_Cientifica", "Operaciones_básicas_en_notación_científica.mp4"),
    (17, "Truco_Dominar_Cifras_Significativas", "El_truco_para_dominar_las_cifras_significativas.mp4"),
    (18, "Como_Operar_Cifras_Significativas", "Cómo_operar_con_cifras_significativas.mp4"),
    (19, "Analisis_Dimensional_Error_NASA_125_Millones", "Análisis_Dimensional__El_Error_que_le_Costó_a_la_NASA_125_Millo.mp4"),
    (20, "Metodo_Tres_Pasos_Estequiometria", "El_método_de_tres_pasos_para_estequiometría.mp4"),
]

print("Cargando modelo Faster-Whisper (small, cpu, int8)...")
model = WhisperModel("small", device="cpu", compute_type="int8")

manifest = {}

for num, slug, filename in REELS_SPECS:
    src_file = SRC_DIR / filename
    if not src_file.exists():
        print(f"ERROR: No se encontró archivo para Reel {num}: {src_file}")
        continue

    workdir = OUTPUTS_DIR / f"reel_{num:02d}_zenit_pipeline"
    workdir.mkdir(parents=True, exist_ok=True)
    words_file = workdir / "04_words.json"

    # Extraer audio mono a 16kHz
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

    print(f"Reel {num:02d} completado en {dt}s. Palabras: {len(words_list)}. Ultima palabra en: {last_word_end:.2f}s -> end_trim: {end_trim:.2f}s")
    print(f"Texto inicial: {text_concat[:100]}...")
    print(f"Texto final: ...{text_concat[-100:]}")

    manifest[num] = {
        "slug": slug,
        "filename": filename,
        "total_words": len(words_list),
        "last_word_end": round(last_word_end, 2),
        "end_trim": end_trim,
        "text": text_concat
    }

manifest_path = OUTPUTS_DIR / "grupo_2_manifest_01_to_20.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\nManifest de Grupo 2 guardado en {manifest_path}")
