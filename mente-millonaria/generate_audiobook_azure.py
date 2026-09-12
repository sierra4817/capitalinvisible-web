#!/usr/bin/env python3
"""
generate_audiobook_azure.py
Genera los 29 mp3 del audiolibro de CPM a partir de capitulos_data.js,
usando la API oficial de Azure AI Speech (licencia comercial correcta,
a diferencia de edge-tts). Textos largos se dividen por parrafos y los
mp3 resultantes se concatenan en uno solo por capitulo.

Uso:
    python generate_audiobook_azure.py --api-key TU_CLAVE --region switzerlandnorth
    python generate_audiobook_azure.py --api-key TU_CLAVE --region switzerlandnorth --force
    python generate_audiobook_azure.py --api-key TU_CLAVE --region switzerlandnorth --solo 00_prologo
"""
import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from xml.sax.saxutils import escape

ARCHIVO_DATOS = "capitulos_data.js"
VOZ_POR_DEFECTO = "es-ES-AlvaroNeural"
MAX_CARACTERES = 9000


def cargar_capitulos():
    if not os.path.isfile(ARCHIVO_DATOS):
        print(f"No encuentro '{ARCHIVO_DATOS}'. Ejecuta este script desde la carpeta raiz del proyecto.")
        sys.exit(1)
    with open(ARCHIVO_DATOS, encoding="utf-8") as f:
        contenido = f.read()
    m = re.search(r"const\s+CAPITULOS\s*=\s*(\[.*\])", contenido, flags=re.DOTALL)
    if not m:
        print(f"No pude leer la lista CAPITULOS dentro de '{ARCHIVO_DATOS}'.")
        sys.exit(1)
    return json.loads(m.group(1))


def dividir_en_parrafos(texto, max_chars):
    oraciones = texto.split(". ")
    partes = []
    actual = ""
    for o in oraciones:
        candidato = (actual + ". " + o) if actual else o
        if len(candidato) > max_chars and actual:
            partes.append(actual.strip())
            actual = o
        else:
            actual = candidato
    if actual.strip():
        partes.append(actual.strip())
    return partes


def obtener_token(api_key, region):
    url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    req = urllib.request.Request(url, method="POST", headers={"Ocp-Apim-Subscription-Key": api_key})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")


def sintetizar(texto, ruta_salida, api_key, region, voz):
    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    texto_seguro = escape(texto)
    ssml = (
        "<speak version='1.0' xml:lang='es-ES'>"
        f"<voice xml:lang='es-ES' xml:gender='Male' name='{voz}'>{texto_seguro}</voice>"
        "</speak>"
    )
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3",
        "User-Agent": "cpm-audiolibro",
    }
    req = urllib.request.Request(url, data=ssml.encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        audio = resp.read()
    os.makedirs(os.path.dirname(ruta_salida) or ".", exist_ok=True)
    with open(ruta_salida, "wb") as f:
        f.write(audio)


def main():
    parser = argparse.ArgumentParser(description="Genera el audiolibro de CPM con Azure AI Speech")
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--voz", default=VOZ_POR_DEFECTO)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--solo", metavar="ID")
    args = parser.parse_args()

    capitulos = cargar_capitulos()
    if args.solo:
        capitulos = [c for c in capitulos if c["id"] == args.solo]
        if not capitulos:
            print(f"No encontre ningun capitulo con id '{args.solo}'.")
            sys.exit(1)

    total = len(capitulos)
    generados = 0
    saltados = 0
    fallidos = 0

    for i, cap in enumerate(capitulos, start=1):
        ruta_salida = cap["audio"]
        texto = " ".join(cap["oraciones"])

        if os.path.isfile(ruta_salida) and not args.force:
            print(f"[{i:02d}/{total}] {cap['id']:20s} ya existe, se omite")
            saltados += 1
            continue

        print(f"[{i:02d}/{total}] {cap['id']:20s} generando... ({len(texto)} caracteres)", end="")

        try:
            if len(texto) <= MAX_CARACTERES:
                sintetizar(texto, ruta_salida, args.api_key, args.region, args.voz)
            else:
                partes = dividir_en_parrafos(texto, MAX_CARACTERES)
                print(f"  [{len(partes)} partes]", end="")
                rutas_parciales = []
                for j, parte in enumerate(partes):
                    ruta_parcial = f"{ruta_salida}.part{j}.tmp"
                    sintetizar(parte, ruta_parcial, args.api_key, args.region, args.voz)
                    rutas_parciales.append(ruta_parcial)
                os.makedirs(os.path.dirname(ruta_salida) or ".", exist_ok=True)
                with open(ruta_salida, "wb") as out:
                    for rp in rutas_parciales:
                        with open(rp, "rb") as f:
                            out.write(f.read())
                        os.remove(rp)
            print("  OK")
            generados += 1
        except urllib.error.HTTPError as e:
            print(f"  ERROR HTTP {e.code}: {e.read().decode(errors='replace')[:200]}")
            fallidos += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            fallidos += 1

    print(f"\nListo. Generados: {generados} | Ya existian: {saltados} | Fallidos: {fallidos} | Total: {total}")


if __name__ == "__main__":
    main()
