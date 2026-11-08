"""
viralforge/render/multicam.py
==============================
Motor de Juegos de Cámara Dinámicos y Ritmo Visual Multicámara para ViralForge / Academia Zenit.

Genera cortes rítmicos estilo producción Netflix / Videoclip (cada 3.5 - 4.2 segundos) para mantener
la dopamina visual y la retención del espectador:
- CAM 1: Plano General 1.0x (Establecimiento y relación orador-pizarra).
- CAM 2: Plano Medio Orador 1.14x (Enfoque en orador y contacto visual cercano).
- CAM 3: Plano Detalle Pizarra 1.22x - 1.26x (Acercamiento a la tiza, fórmulas y cálculos).
- Barra Dorada de Progreso / Retención en el borde superior (h=12px, #FFE45E).
- Retorna la lista de cortes para inyección automática de SFX (camera_shutter / pop / whoosh).
"""
from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger("viralforge.render.multicam")


def generate_camera_intervals(
    total_duration: float,
    pattern: tuple[str, ...] = ("speaker", "board", "wide", "board"),
    speaker_duration: float = 3.6,
    board_duration: float = 4.2,
    wide_duration: float = 3.8,
) -> tuple[list[tuple[float, float]], list[tuple[float, float]], list[float]]:
    """
    Genera los intervalos temporales para cada ángulo de cámara y los puntos exactos de corte.

    Returns:
        (speaker_intervals, board_intervals, cut_timestamps)
    """
    speaker_intervals: list[tuple[float, float]] = []
    board_intervals: list[tuple[float, float]] = []
    cut_timestamps: list[float] = []

    curr_t = 0.0
    pat_idx = 0
    num_pat = len(pattern)

    while curr_t < total_duration:
        mode = pattern[pat_idx % num_pat]
        if mode == "speaker":
            seg_len = speaker_duration
        elif mode == "board":
            seg_len = board_duration
        else:
            seg_len = wide_duration

        end_t = min(curr_t + seg_len, total_duration)

        if mode == "speaker":
            speaker_intervals.append((round(curr_t, 2), round(end_t, 2)))
        elif mode == "board":
            board_intervals.append((round(curr_t, 2), round(end_t, 2)))
        # Si es 'wide', no se superpone nada sobre CAM 1

        if curr_t > 0.05:
            cut_timestamps.append(round(curr_t, 2))

        curr_t = end_t
        pat_idx += 1

    return speaker_intervals, board_intervals, cut_timestamps


def build_multicam_filter_complex(
    input_label: str,
    output_label: str,
    duration: float,
    width: int = 1080,
    height: int = 1920,
    speaker_scale: float = 1.14,
    board_scale: float = 1.24,
    enable_progress_bar: bool = True,
    progress_bar_color: str = "#FFE45E",
    progress_bar_height: int = 18,
    progress_bar_y: int = 1180,
    pattern: tuple[str, ...] = ("speaker", "board", "wide", "board"),
    enable_camera_cuts: bool = True,
) -> tuple[list[str], list[float]]:
    """
    Construye las cadenas del filter_complex de FFmpeg para aplicar los cortes multicámara
    y la barra inferior de retención y progreso en tiempo real (debajo de los subtítulos).

    Returns:
        (filter_chains, cut_timestamps)
    """
    if not enable_camera_cuts:
        chains: list[str] = []
        if enable_progress_bar:
            # Barra de progreso dinámica que avanza visiblemente en tiempo real (de izquierda a derecha)
            chains.append(f"[{input_label}]drawbox=x=0:y={progress_bar_y}:w=iw:h={progress_bar_height}:color=0x0F172A@0.85:t=fill[v_track]")
            chains.append(f"color=c={progress_bar_color}:s={width}x{progress_bar_height}:d={duration:.2f}[p_bar]")
            chains.append(f"[v_track][p_bar]overlay=x='-w+(t/{duration:.2f})*w':y={progress_bar_y}[{output_label}]")
        else:
            chains.append(f"[{input_label}]null[{output_label}]")
        return chains, []

    speaker_intervals, board_intervals, cut_timestamps = generate_camera_intervals(
        duration, pattern=pattern
    )

    sp_enable = "+".join(f"between(t,{s:.2f},{e:.2f})" for s, e in speaker_intervals) if speaker_intervals else "0"
    bd_enable = "+".join(f"between(t,{s:.2f},{e:.2f})" for s, e in board_intervals) if board_intervals else "0"

    sp_w = f"iw/{speaker_scale:.3f}"
    sp_h = f"ih/{speaker_scale:.3f}"
    bd_w = f"iw/{board_scale:.3f}"
    bd_h = f"ih/{board_scale:.3f}"

    chains: list[str] = []

    # 1. Separar la base en 3 ramas de cámara
    chains.append(f"[{input_label}]split=3[v_cam_wide][v_raw_sp][v_raw_bd]")

    # 2. CAM 2 (Orador): recorte centrado/ligeramente superior + re-escalado
    chains.append(
        f"[v_raw_sp]crop={sp_w}:{sp_h}:iw*0.04:ih*0.02,scale={width}:{height}[v_cam_speaker]"
    )

    # 3. CAM 3 (Pizarra): recorte enfocado a la zona de fórmulas/tiza + re-escalado
    chains.append(
        f"[v_raw_bd]crop={bd_w}:{bd_h}:iw*0.10:ih*0.06,scale={width}:{height}[v_cam_board]"
    )

    # 4. Alternancia dinámica mediante overlays condicionados por tiempo
    chains.append(
        f"[v_cam_wide][v_cam_speaker]overlay=0:0:enable='{sp_enable}'[v_mc_step1]"
    )
    chains.append(
        f"[v_mc_step1][v_cam_board]overlay=0:0:enable='{bd_enable}'[v_mc_switched]"
    )

    # 5. Barra de Retención Psicológica y Progreso Dinámico (debajo de los subtítulos)
    if enable_progress_bar:
        # Barra de progreso dinámica que avanza visiblemente en tiempo real (de izquierda a derecha)
        chains.append(f"[v_mc_switched]drawbox=x=0:y={progress_bar_y}:w=iw:h={progress_bar_height}:color=0x0F172A@0.85:t=fill[v_track]")
        chains.append(f"color=c={progress_bar_color}:s={width}x{progress_bar_height}:d={duration:.2f}[p_bar]")
        chains.append(f"[v_track][p_bar]overlay=x='-w+(t/{duration:.2f})*w':y={progress_bar_y}[{output_label}]")
    else:
        chains.append(f"[v_mc_switched]null[{output_label}]")

    return chains, cut_timestamps
