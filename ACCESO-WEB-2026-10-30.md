# Acceso web conectado — 30 de octubre de 2026

Abrir https://avatars.sistemazenit.com/ . El sitio requiere una clave compartida de operador. La clave está en `data/private/web-access.key` de este proyecto (carpeta excluida de Git); abrir ese archivo localmente y copiarla al formulario. No compartirla en chats ni incorporarla al código. La sesión dura seis horas; el botón «Cerrar sesión» permite salir. No es un sistema multiusuario con roles.

## Conexión aplicada y comprobada

- Cloudflare Tunnel `avatars-oracle`, ID `d54c4cc6-5495-470a-adde-3e52d2adef13`, conector saludable en Oracle ARM64.
- Hostnames `avatars.sistemazenit.com` y `origin-avatars.sistemazenit.com` hacia `http://127.0.0.1:8766`.
- Entrada autenticada separada `viralforge-web`: firma de sesiones, cookie Secure/HttpOnly/SameSite=Strict, control de origen para escrituras, límite de carga 64 MB y diez fallos de acceso por minuto globales al proceso. Su reinicio borra el contador; no es defensa distribuida contra ataques.
- API residente sigue en `127.0.0.1:8765`. Ambos puertos permanecen en loopback. SSH y MCP conservados; no se habilitó render desatendido MCP.
- Túnel temporal `viralforge-tunnel` desactivado tras probar la conexión estable. Su configuración se conserva.
- El dominio se desvinculó del proyecto estático Cloudflare Pages `avatars` y se creó su CNAME al túnel. Pages y sus despliegues permanecen disponibles en `avatars-1qo.pages.dev`; los futuros despliegues de Pages no actualizan la aplicación que sirve Oracle.
- Credencial del túnel transferida en memoria y guardada únicamente en `/opt/viralforge/private/tunnel.token`, permisos 600. Clave de acceso web en `/opt/viralforge/private/web-access.key`, con copia local privada para el operador. No se imprimieron secretos.

## Pruebas

37 pruebas locales correctas; cinco pruebas nuevas de acceso también pasaron en Oracle antes de la publicación. Corrección posterior de Referrer-Policy verificada con las cinco pruebas locales y con un formulario real en navegador. La política `no-referrer` bloqueaba el formulario por su Origin; se cambió a `same-origin`, manteniendo el rechazo de sitios ajenos.

Desde Internet, en los dos hostnames: API anónima 401; formulario autenticado 303; API y estudio autenticados 200; escritura de origen ajeno 403; video con Range 206. En navegador: inicio de sesión real, datos del catálogo, galería y reproducción de `var_4e037664f9` (7,43 s, readyState 4, sin error), cierre de sesión y nuevo acceso correctos. La interfaz ignora URLs antiguas guardadas para estos dos hostnames y utiliza el mismo origen.

La muestra y siete archivos se transfirieron a Oracle, verificando hashes y calidad, sin render nuevo. Se añadió solamente el producto técnico asociado, conservando el catálogo anterior. No se ejecutaron pruebas GPU nuevas ni se certificaron las demás funciones históricas que anuncia la interfaz.

## Reversión

Antes de cambiar rutas, comprobar que no haya renders activos. Para regresar al sitio estático: retirar la ruta/CNAME de `avatars.sistemazenit.com` del túnel y volver a asociar ese dominio al proyecto Pages `avatars`. Conservar datos y despliegues. No reactivar un túnel que exponga directamente la API sin autenticación.

Los servicios añadidos son `viralforge-web` y `viralforge-cloudflare`; sus archivos están en `/etc/systemd/system/`. Se pueden detener y deshabilitar para retirar el acceso web manteniendo `viralforge` y SSH/MCP. El respaldo de la interfaz es `viralforge/ui/app.before-managed-web.js`; el respaldo previo a la corrección del formulario es `viralforge/web_gateway.before-form-fix.py` dentro de la versión `20261030-incremental` (no restaurar ese último sin corregir el formulario).

## Límites pendientes

La conexión pública autenticada queda comprobada. La reproducción técnica no equivale a escuchar y aprobar pronunciación y sincronización labial; esa revisión audiovisual humana sigue pendiente. Tampoco se ha confirmado una oferta real para una campaña comercial. VoiceStudio queda excluido por decisión del usuario.

Evidencias: `evidencias/web-20261030/` contiene resultados HTTP y capturas. La revisión automática rechazó inicialmente una copia local de la credencial de túnel; se resolvió mediante transferencia en memoria al VPS. No queda un bloqueo de aprobación por ese motivo.
