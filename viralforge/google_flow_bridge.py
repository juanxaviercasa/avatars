"""
viralforge/google_flow_bridge.py
================================
Conector Automatizado para Google Flow (https://flow.google.com/) mediante Playwright y Perfil Persistente de Chrome.

Características:
1. Perfil Persistente Seguro:
   - Almacena cookies de sesión de Google en C:\\Users\\cabel\\.gemini\\flow_chrome_profile
   - Permite autenticarse una sola vez (--setup) y reutilizar la sesión en segundo plano.
2. Modo Generación Automatizada:
   - Navega a Google Flow, ingresa el prompt educativo 9:16, espera la síntesis y descarga la imagen en alta definición.
   - Registra automáticamente el activo en assets/images/pool/<categoria>/
3. Fallback Resiliente (Zero-Crash):
   - Si Google Flow está cerrado o la sesión expiró, recurre automáticamente al Thematic Asset Pool sin detener el render del video.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

from .config import settings
from .render import background_pool

log = logging.getLogger("viralforge.google_flow_bridge")

PROFILE_DIR = Path("C:/Users/cabel/.gemini/flow_chrome_profile")
FLOW_URL = "https://flow.google.com/"


async def setup_flow_login() -> None:
    """
    Abre una ventana visible de Google Chrome con el perfil persistente de Flow.
    El usuario inicia sesión con su cuenta de Google una sola vez.
    """
    from playwright.async_api import async_playwright

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    print("\n=================================================================")
    print(" INICIALIZANDO SESION DE GOOGLE FLOW (GOOGLE LABS)")
    print("=================================================================")
    print("Se abrirá una ventana de Google Chrome.")
    print("1. Inicia sesión con tu cuenta de Google.")
    print("2. Acepta los términos de Google Flow / ImageFX.")
    print("3. Una vez dentro de la interfaz, cierra el navegador.")
    print(f"Tu sesión quedará guardada de forma permanente en:\n{PROFILE_DIR}")
    print("=================================================================\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = await browser.new_page()
        await page.goto(FLOW_URL, wait_until="networkidle")
        
        print("Esperando a que cierres la ventana tras iniciar sesión...")
        # Mantener abierto hasta que el usuario cierre el navegador
        try:
            while len(browser.pages) > 0:
                await asyncio.sleep(1)
        except Exception:
            pass
        print("Sesión de Google Flow guardada exitosamente.")


async def generate_flow_image_async(
    prompt: str,
    category: str = "admision_general",
    timeout_s: float = 60.0
) -> Path:
    """
    Automatiza la generación de una imagen en Google Flow usando la sesión persistente.
    Si la sesión no está lista o hay timeout, recurre al pool temático sin frenar el flujo.
    """
    from playwright.async_api import async_playwright

    if not PROFILE_DIR.exists() or not any(PROFILE_DIR.iterdir()):
        log.warning("Perfil de Google Flow no configurado. Usando Thematic Asset Pool...")
        return background_pool.get_thematic_background(category)

    log.info("Conectando a Google Flow con sesión persistente...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                channel="chrome",
                headless=True,
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = await browser.new_page()
            await page.goto(FLOW_URL, timeout=30000, wait_until="domcontentloaded")

            # Verificar si estamos logueados o nos pide Sign in
            content = await page.content()
            if "Sign in" in content or "Iniciar sesión" in content:
                log.warning("La sesión de Google Flow expiró. Usando Thematic Asset Pool...")
                await browser.close()
                return background_pool.get_thematic_background(category)

            # Buscar textarea o input de prompt en Google Flow / ImageFX
            input_selector = "textarea, input[type='text'], [contenteditable='true']"
            prompt_input = await page.wait_for_selector(input_selector, timeout=15000)
            if not prompt_input:
                log.warning("No se encontró el cuadro de prompt en Google Flow.")
                await browser.close()
                return background_pool.get_thematic_background(category)

            # Ingresar prompt con aspecto vertical 9:16
            full_prompt = f"{prompt}, vertical aspect ratio 9:16, cinematic laboratory lighting, 8k, photorealistic"
            await prompt_input.fill(full_prompt)
            await page.keyboard.press("Enter")

            log.info("Prompt enviado a Google Flow. Esperando renderizado...")
            
            # Esperar a que aparezca la imagen generada (esperar tag img nuevo o botón de descarga)
            await asyncio.sleep(12)  # Tiempo típico de generación en Imagen 3
            
            # Buscar la imagen resultante con mayor resolución
            imgs = await page.query_selector_all("img")
            best_img_src = None
            for img in imgs:
                src = await img.get_attribute("src")
                if src and ("googleusercontent.com" in src or "blob:" in src or "data:image" in src):
                    best_img_src = src
                    break

            temp_dest = settings.cache_dir / f"flow_gen_{int(time.time())}.jpg"
            if best_img_src and best_img_src.startswith("http"):
                # Descargar vía urllib o captura de elemento
                import urllib.request
                req = urllib.request.Request(best_img_src, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req) as resp:
                    temp_dest.write_bytes(resp.read())
            else:
                # Captura directa del viewport o contenedor si no hay link directo
                canvas_or_container = await page.query_selector("main, [role='main'], canvas")
                if canvas_or_container:
                    await canvas_or_container.screenshot(path=str(temp_dest))
                else:
                    await page.screenshot(path=str(temp_dest))

            await browser.close()

            if temp_dest.exists() and temp_dest.stat().st_size > 10000:
                final_path = background_pool.register_new_background(temp_dest, category)
                temp_dest.unlink(missing_ok=True)
                log.info("¡Imagen generada con Google Flow y agregada al pool!: %s", final_path)
                return final_path
            else:
                log.warning("No se pudo extraer la imagen completa de Flow. Usando Asset Pool...")
                return background_pool.get_thematic_background(category)

    except Exception as e:
        log.warning("Excepción interactuando con Google Flow (%s). Usando Asset Pool...", e)
        return background_pool.get_thematic_background(category)


def get_hook_background(subject: str, custom_prompt: str | None = None, use_flow: bool = False) -> Path:
    """
    Punto de entrada unificado para obtener el fondo del hook:
    - Si use_flow=True y hay prompt: intenta generar con Google Flow.
    - Por defecto o ante cualquier contingencia: devuelve un fondo temático de alta resolución del Asset Pool.
    """
    if use_flow and custom_prompt:
        try:
            return asyncio.run(generate_flow_image_async(custom_prompt, category=subject))
        except Exception as e:
            log.warning("Fallo al invocar Flow: %s", e)
    
    return background_pool.get_thematic_background(subject)


def main():
    parser = argparse.ArgumentParser(description="Google Flow Automation Bridge")
    parser.add_argument("--setup", action="store_true", help="Abre Chrome para iniciar sesión en Google Flow")
    parser.add_argument("--test-pool", action="store_true", help="Muestra estadísticas del Asset Pool")
    parser.add_argument("--subject", type=str, default="quimica", help="Tema del fondo a obtener")
    args = parser.parse_args()

    if args.setup:
        asyncio.run(setup_flow_login())
    elif args.test_pool:
        print("ESTADISTICAS DEL THEMATIC ASSET POOL:")
        print(background_pool.get_pool_stats())
    else:
        bg = get_hook_background(args.subject)
        print(f"Fondo seleccionado para '{args.subject}': {bg}")


if __name__ == "__main__":
    main()
