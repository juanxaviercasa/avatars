"""Paso 6 — Ensamblado integral de ayudas visuales, marca de agua y cierre al video.

Toma:
1. Video base saneado (Paso 2).
2. Ayudas visuales generadas a medida exacta (Paso 5) con sus coordenadas y tiempos.
3. Marca de agua oficial de Sistema Zenit (Paso 7).
4. Pantalla de cierre y CTA con www.sistemazenit.com (Pasos 8 y 9).
5. Barra de progreso dorada delimitada (sin desborde derecho).
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any

from .brand import FRAME_H, FRAME_W
from .step4_narration import VisualSlot
from .step5_fit import FitResult
from .step7_watermark import create_watermark_pill, get_watermark_placement
from .step8_9_closing_cta import create_closing_cta_card

log = logging.getLogger("viralforge.zenit_pipeline.assemble")


def assemble_zenit_video(
    base_video: Path,
    slots: list[VisualSlot],
    fitted_visuals: dict[str, FitResult],
    workdir: Path,
    output_path: Path,
    outro_card_img: Path | None = None,
    cta_duration: float = 6.0,
    action_prompt: str = "ZENIT",
) -> Path:
    """Ensambla el video completo con todos los elementos en capas seguras."""
    base_video = Path(base_video).resolve()
    workdir = Path(workdir).resolve()
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Preparar imagen de marca de agua oficial (Paso 7)
    watermark_path = workdir / "watermark_pill.png"
    create_watermark_pill(watermark_path)
    wm_pos = get_watermark_placement(FRAME_W, FRAME_H)
    
    # 2. Preparar imagen de cierre / CTA (Pasos 8 y 9)
    if outro_card_img is None or not Path(outro_card_img).exists():
        outro_card_img = workdir / "closing_cta_card.png"
        create_closing_cta_card(outro_card_img, action_prompt=action_prompt)
        
    # Obtener duración del video base
    import json
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(base_video)],
        capture_output=True, text=True, check=True
    )
    base_dur = float(json.loads(probe.stdout)["format"]["duration"])
    total_dur = base_dur + cta_duration
    
    # Construcción del grafo de filtros FFmpeg
    inputs = ["-i", str(base_video)]
    
    # Overlay de marca de agua
    wm_idx = len(inputs) // 2
    inputs.extend(["-i", str(watermark_path)])
    
    # Overlays educativos ajustados
    overlay_indices: list[dict[str, Any]] = []
    for slot in slots:
        if slot.status != "ok" or not slot.zone:
            continue
        spec_id = slot.spec.id
        fit = fitted_visuals.get(spec_id)
        if not fit or not fit.ok or not fit.path:
            continue
            
        idx = len(inputs) // 2
        inputs.extend(["-i", str(fit.path)])
        
        # Centrar la ayuda visual dentro de su zona libre asignada
        zx, zy, zw, zh = slot.zone.as_rect()
        cx = zx + (zw - fit.width) // 2
        cy = zy + (zh - fit.height) // 2
        
        overlay_indices.append({
            "input_idx": idx,
            "x": cx,
            "y": cy,
            "start": slot.start,
            "end": slot.end,
        })
        
    filter_steps = [
        f"[0:v]scale={FRAME_W}:{FRAME_H}:force_original_aspect_ratio=decrease,"
        f"pad={FRAME_W}:{FRAME_H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v_base]"
    ]
    
    # Componer marca de agua superior permanente durante la lección
    last_v = "v_base"
    filter_steps.append(
        f"[{last_v}][{wm_idx}:v]overlay={wm_pos['x']}:{wm_pos['y']}:"
        f"enable='lt(t,{base_dur:.3f})':eof_action=repeat[v_wm]"
    )
    last_v = "v_wm"
    
    # Componer cada ayuda visual en su intervalo exacto
    for item in overlay_indices:
        i_idx = item["input_idx"]
        ox = item["x"]
        oy = item["y"]
        t0 = item["start"]
        t1 = item["end"]
        next_v = f"v_ov_{i_idx}"
        filter_steps.append(
            f"[{last_v}][{i_idx}:v]overlay={ox}:{oy}:"
            f"enable='between(t,{t0:.3f},{t1:.3f})':eof_action=repeat[{next_v}]"
        )
        last_v = next_v
        
    # Barra de retención delimitada estrictamente a [90, 990] sin desborde
    # Easing cuadrático suave
    filter_steps.append(
        f"color=c=0xFFE45E:s=900x24:d={base_dur:.3f}[c_gold];"
        f"color=c=0x0B1323:s=900x24:d={base_dur:.3f}[c_cover];"
        f"[c_gold][c_cover]overlay=x='900*(1-pow(1-min(1,max(0,t/{base_dur:.3f})),1.65))':y=0[pbar_inner]"
    )
    filter_steps.append(
        f"[{last_v}]drawbox=x=87:y=1799:w=906:h=32:color=0x0B1323@0.88:t=fill:enable='lt(t,{base_dur:.3f})',"
        f"drawbox=x=87:y=1799:w=906:h=2:color=0xFFE45E@0.40:t=fill:enable='lt(t,{base_dur:.3f})'[v_track]"
    )
    filter_steps.append(
        f"[v_track][pbar_inner]overlay=x=90:y=1803:enable='lt(t,{base_dur:.3f})':eof_action=pass[v_lesson]"
    )
    
    # Paso 8 y 9: Concatenar pantalla de cierre
    cta_idx = len(inputs) // 2
    inputs.extend(["-loop", "1", "-t", f"{cta_duration:.3f}", "-framerate", "30", "-i", str(outro_card_img)])
    
    filter_steps.append(
        f"[{cta_idx}:v]scale={FRAME_W}:{FRAME_H}:flags=lanczos,format=yuv420p,setsar=1[v_cta]"
    )
    filter_steps.append(
        f"[v_lesson][v_cta]concat=n=2:v=1:a=0[v_final]"
    )
    
    # Audio: audio original seguido de silencio/cierre
    filter_steps.append(
        f"[0:a]apad=pad_dur={cta_duration:.3f}[a_final]"
    )
    
    vf = ";".join(filter_steps)
    staging_file = output_path.with_suffix(".staging.mp4")
    
    cmd = [
        "ffmpeg", "-v", "error", "-y",
        *inputs,
        "-filter_complex", vf,
        "-map", "[v_final]",
        "-map", "[a_final]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-map_metadata", "-1",
        "-fflags", "+bitexact",
        "-flags:v", "+bitexact",
        "-flags:a", "+bitexact",
        "-movflags", "+faststart",
        str(staging_file),
    ]
    
    subprocess.run(cmd, check=True)
    
    if output_path.exists():
        output_path.unlink()
    staging_file.rename(output_path)
    
    log.info("Video ensamblado con éxito en: %s", output_path)
    return output_path
