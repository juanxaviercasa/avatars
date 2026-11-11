import json, subprocess, time
from pathlib import Path
from faster_whisper import WhisperModel

SRC_DIR = Path(r"C:\Users\cabel\Videos\reels-quimica")
OUTPUTS_DIR = Path("outputs/quimica_piloto_10")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

REELS_51_TO_60 = [
    (51, "Reactivo_Limitante_Sin_Errores", "Cómo_identificar_el_reactivo_limitante_sin_errores.mp4"),
    (52, "Diagramas_Energia_Activacion", "Cómo_leer_diagramas_de_energía_química.mp4"),
    (53, "Constante_Equilibrio_Kc_Solidos", "Cómo_formular_la_constante_de_equilibrio_sin_fallar.mp4"),
    (54, "Comparacion_Q_vs_K_Equilibrio", "El_truco_definitivo_para_comparar_Q_y_K.mp4"),
    (55, "Catalizadores_Velocidad_vs_Equilibrio", "Por_qué_los_catalizadores_no_alteran_el_equilibrio.mp4"),
    (56, "Principio_Le_Chatelier_Balanza", "Principio_de_Le_Châtelier__Truco_de_la_Balanza.mp4"),
    (57, "Calculo_Mental_pH_Logaritmos", "Truco_mental_para_calcular_el_pH.mp4"),
    (58, "Pares_Acido_Base_Conjugados", "Cómo_Identificar_Pares_Ácido-Base_Conjugados.mp4"),
    (59, "Flechas_Reaccion_Acido_Fuerte_Debil", "Cómo_las_flechas_de_reacción_cambian_tu_cálculo_de_pH.mp4"),
    (60, "Producto_Ionico_Agua_Kw_pH_pOH", "Cómo_funciona_el_producto_iónico_del_agua.mp4"),
]

model = WhisperModel("small", device="cpu", compute_type="int8")

manifest = {}

for num, slug, filename in REELS_51_TO_60:
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

report_path = OUTPUTS_DIR / "batch_51_to_60_manifest.json"
report_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nManifest guardado en: {report_path}")
