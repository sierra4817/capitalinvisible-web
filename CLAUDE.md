# CLAUDE.md

## Regla estricta de comunicación

Debes comunicarte, explicar y documentar siempre en español. Sé conciso, técnico y directo.

## Resumen en audio tras cada respuesta

Al terminar de responder, genera un resumen de 2 frases de lo que hiciste y pásalo a
`/usr/local/bin/tts-say` (NO `audio-web`: ese script escribe dentro del repo git y
anuncia una URL pública en el puerto 80 que no existe en este servidor).
`tts-say` publica el audio en `/root/tts-audio/` para `speak.html`, servido de forma
privada en `127.0.0.1:8081` (acceso vía túnel SSH, ver conversación previa).
