import json, subprocess, time
from pathlib import Path
from faster_whisper import WhisperModel

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
OUTPUTS_DIR = Path("outputs/quimica_piloto_10")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_41_TO_50 = [
    (41, "Fuerzas_Intermoleculares_Clave", "Cómo_dominar_las_fuerzas_intermoleculares.mp4"),
    (42, "Misterio_100C_Agua_Puentes_Hidrogeno", "El_misterio_de_los_100_°C_del_agua.mp4"),
    (43, "Viscosidad_y_Tension_Superficial", "Fuerzas_intermoleculares__Viscosidad_y_tensión_superficial.mp4"),
    (44, "Diagrama_de_Fases_Punto_Triple", "Cómo_Interpretar_un_Diagrama_de_Fases.mp4"),
    (45, "Ley_de_Henry_Gases_Liquidos", "Cómo_funciona_la_Ley_de_Henry.mp4"),
    (46, "Molaridad_vs_Molalidad_Trampa_Termica", "La_trampa_térmica_de_la_Molaridad.mp4"),
    (47, "Propiedades_Coligativas_Presion_Vapor", "Cómo_el_soluto_bloquea_al_disolvente.mp4"),
    (48, "Factor_van_t_Hoff_Coligativas", "La_trampa_del_factor_de_van__t_Hoff.mp4"),
    (49, "Reactivo_Limitante_Metodo_Division", "Cómo_identificar_el_reactivo_limitante_sin_fallar.mp4"),
    (50, "Reactivo_Limitante_Fundamentos", "Cómo_Funciona_el_Reactivo_Limitante_en_Química.mp4"),
]

model = WhisperModel("small", device="cpu", compute_type="int8")

manifest = {}

for num, slug, filename in REELS_41_TO_50:
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

report_path = OUTPUTS_DIR / "batch_41_to_50_manifest.json"
report_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nManifest guardado en: {report_path}")
