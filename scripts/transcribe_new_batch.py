import json, subprocess, time
from pathlib import Path
from faster_whisper import WhisperModel

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
OUTPUTS_DIR = Path("outputs/quimica_piloto_10")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

NEW_REELS = [
    (11, "Numeros_Oxidacion", "Cómo_calcular_números_de_oxidación_en_segundos.mp4"),
    (12, "Balanceo_Ecuaciones", "Cómo_Ajustar_Ecuaciones_Químicas_Sin_Adivinar.mp4"),
    (13, "Rendimiento_Reaccion", "Por_Qué_el_Rendimiento_Químico_Nunca_es_del_100_.mp4"),
    (14, "Diluciones_M1V1_M2V2", "Cómo_calcular_diluciones_con_M1V1=M2V2.mp4"),
    (15, "Ecuaciones_Ionicas_Netas", "Escribir_ecuaciones_iónicas_netas_sin_fallos.mp4"),
    (16, "Agua_Pura_Conductividad", "Por_qué_el_agua_pura_no_conduce_electricidad.mp4"),
    (17, "Leyes_Gases_Boyle_Charles", "El_truco_visual_para_las_leyes_de_los_gases.mp4"),
    (18, "Gas_Ideal_PV_nRT", "El_truco_definitivo_para_la_ecuación_de_los_gases.mp4"),
    (19, "Presion_Parcial_Dalton", "El_Truco_Definitivo_para_la_Presión_Parcial.mp4"),
    (20, "Gases_Reales_van_der_Waals", "Por_qué_fallan_los_gases_ideales.mp4"),
]

model = WhisperModel("small", device="cpu", compute_type="int8")

manifest = {}

for num, slug, filename in NEW_REELS:
    src_file = SRC_DIR / filename
    if not src_file.exists():
        print(f"ERROR: {src_file} no existe")
        continue

    workdir = OUTPUTS_DIR / f"reel_{num:02d}_zenit_pipeline"
    workdir.mkdir(parents=True, exist_ok=True)
    words_file = workdir / "04_words.json"

    # Extract audio
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
                        "prob": round(w.probability, 3),
                    })

    words_file.write_text(json.dumps(words_list, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Analyze total duration and trims
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(src_file)], capture_output=True, text=True)
    total_dur = float(json.loads(probe.stdout)["format"]["duration"])
    
    first_w = words_list[0] if words_list else {"start": 0.0, "text": ""}
    last_w = words_list[-1] if words_list else {"end": total_dur, "text": ""}

    # Suggested end_trim: last word end + 0.35s
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
    print(f"  -> {len(words_list)} palabras en {time.time()-t0:.1f}s. Primer palabra: '{first_w['text']}' @ {first_w['start']}s | Ultima: '{last_w['text']}' @ {last_w['end']}s | Total: {total_dur:.2f}s | Trim: [{suggested_start:.2f}, {suggested_end:.2f}]")

report_path = OUTPUTS_DIR / "new_batch_11_to_20_manifest.json"
report_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nManifest guardado en: {report_path}")
