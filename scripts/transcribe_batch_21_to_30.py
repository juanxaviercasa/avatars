import json, subprocess, time
from pathlib import Path
from faster_whisper import WhisperModel

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
OUTPUTS_DIR = Path("outputs/quimica_piloto_10")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_21_TO_30 = [
    (21, "Signo_Entalpia_Exo_Endo", "Cómo_interpretar_el_signo_de_la_entalpía.mp4"),
    (22, "Calorimetria_Q_mcDT", "Cómo_no_fallar_en_calorimetría.mp4"),
    (23, "Ley_de_Hess", "El_rompecabezas_de_la_Ley_de_Hess.mp4"),
    (24, "Entalpia_Formacion_Cero_Oculto", "El_Cero_Oculto_en_Termoquímica.mp4"),
    (25, "Efecto_Fotoelectrico_E_hf", "El_Secreto_Cuántico_del_Efecto_Fotoeléctrico.mp4"),
    (26, "Numeros_Cuanticos_n_l_m_s", "Cómo_leer_los_4_números_cuánticos_sin_perderte.mp4"),
    (27, "Configuracion_Electronica_Moeller", "Cómo_Clavar_la_Configuración_Electrónica.mp4"),
    (28, "Anomalias_Configuracion_Cromo_Cobre", "Por_qué_el_Cromo_rompe_las_reglas.mp4"),
    (29, "Radio_Ionico_Cationes_Aniones", "Por_qué_los_cationes_encogen_y_los_aniones_engordan.mp4"),
    (30, "Energia_de_Ionizacion", "Por_Qué_Cuesta_Tanto_Arrancar_un_Electrón__Energía_de_Ionizació.mp4"),
]

model = WhisperModel("small", device="cpu", compute_type="int8")

manifest = {}

for num, slug, filename in REELS_21_TO_30:
    src_file = SRC_DIR / filename
    if not src_file.exists():
        print(f"ERROR: {src_file} no existe")
        continue

    workdir = OUTPUTS_DIR / f"reel_{num:02d}_zenit_pipeline"
    workdir.mkdir(parents=True, exist_ok=True)
    words_file = workdir / "04_words.json"

    # Extraer audio
    wav_path = workdir / "source_audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src_file), "-vn", "-ar", "16000", "-ac", "1", str(wav_path)], check=True)

    print(f"Transcribiendo Reel {num:02d}: {filename}...")
    t0 = time.time()
    segments, info = model.transcribe(str(wav_path), word_timestamps=True, language="es")
    
    words_list = []
    full_text_parts = []
    for s in segments:
        full_text_parts.append(s.text.strip())
        if s.words:
            for w in s.words:
                txt = w.word.strip()
                if txt and "thank" not in txt.lower():
                    words_list.append({
                        "start": round(w.start, 3),
                        "end": round(w.end, 3),
                        "text": txt,
                    })

    words_file.write_text(json.dumps(words_list, indent=2, ensure_ascii=False), encoding="utf-8")
    
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(src_file)], capture_output=True, text=True)
    total_dur = float(json.loads(probe.stdout)["format"]["duration"])
    
    first_w = words_list[0] if words_list else {"start": 0.0, "text": ""}
    last_w = words_list[-1] if words_list else {"end": total_dur, "text": ""}

    suggested_end = min(total_dur - 0.1, round(last_w["end"] + 0.35, 2))
    suggested_start = max(0.0, round(first_w["start"] - 0.2, 2))

    manifest[num] = {
        "slug": slug,
        "filename": filename,
        "total_duration": total_dur,
        "first_word": first_w,
        "last_word": last_w,
        "suggested_start_trim": suggested_start,
        "suggested_end_trim": suggested_end,
        "word_count": len(words_list),
        "full_text": " ".join(full_text_parts),
    }
    print(f"  -> {len(words_list)} palabras en {time.time()-t0:.1f}s. Trim: [{suggested_start:.2f}, {suggested_end:.2f}] sobre {total_dur:.2f}s")

report_path = OUTPUTS_DIR / "batch_21_to_30_manifest.json"
report_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nManifest guardado en: {report_path}")
