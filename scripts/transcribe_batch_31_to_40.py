import json, subprocess, time
from pathlib import Path
from faster_whisper import WhisperModel

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
OUTPUTS_DIR = Path("outputs/quimica_piloto_10")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_31_TO_40 = [
    (31, "Electronegatividad_vs_Afinidad", "Por_Qué_Confundes_Electronegatividad_y_Afinidad_Electrónica.mp4"),
    (32, "Metales_vs_No_Metales", "Cómo_distinguir_metales_y_no_metales.mp4"),
    (33, "Numeros_Oxidacion_Sin_Fallar", "Cómo_calcular_números_de_oxidación_sin_fallar.mp4"),
    (34, "Numeros_Oxidacion_Al_Instante", "Cómo_calcular_números_de_oxidación_al_instante.mp4"),
    (35, "Enlace_Ionico_vs_Covalente", "Diferencias_clave_entre_enlace_iónico_y_covalente.mp4"),
    (36, "Trampas_Regla_Octeto", "Las_trampas_de_la_regla_del_octeto.mp4"),
    (37, "Geometria_Electronica_vs_Molecular", "Cómo_diferenciar_la_geometría_electrónica_y_molecular.mp4"),
    (38, "Hibridacion_sp_sp2_sp3", "Hibridación_sp,_sp2_y_sp3__Cómo_calcularla_en_segundos.mp4"),
    (39, "Polaridad_Molecular_Momento_Dipolar", "El_secreto_de_la_polaridad_molecular.mp4"),
    (40, "Enlaces_Sigma_y_Pi", "Cómo_contar_enlaces_sigma_y_pi_en_segundos.mp4"),
]

model = WhisperModel("small", device="cpu", compute_type="int8")

manifest = {}

for num, slug, filename in REELS_31_TO_40:
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

report_path = OUTPUTS_DIR / "batch_31_to_40_manifest.json"
report_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nManifest guardado en: {report_path}")
