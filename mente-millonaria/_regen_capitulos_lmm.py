# -*- coding: utf-8 -*-
import json, re, os
import azure.cognitiveservices.speech as speechsdk

VOZ = "es-ES-AlvaroNeural"
KEY = os.environ["AZURE_SPEECH_KEY"]
REGION = os.environ["AZURE_SPEECH_REGION"]
IDS = [
    "23_cap_tulo_18_diversificar_no_es_cobard_a",
    "25_cap_tulo_20_el_sistema_fiscal_c_mo_funciona_y_c_mo",
    "26_cap_tulo_21_la_herencia_c_mo_planificar_la_transmi",
]
MAX_CHARS = 9000

with open("capitulos_data.js", encoding="utf-8") as f:
    content = f.read()
m = re.search(r"const\s+CAPITULOS\s*=\s*(\[.*\])", content, flags=re.DOTALL)
capitulos = json.loads(m.group(1))
by_id = {c["id"]: c for c in capitulos}


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def dividir(texto, max_chars):
    oraciones = texto.split(". ")
    partes, actual = [], ""
    for o in oraciones:
        cand = (actual + ". " + o) if actual else o
        if len(cand) > max_chars and actual:
            partes.append(actual.strip())
            actual = o
        else:
            actual = cand
    if actual.strip():
        partes.append(actual.strip())
    return partes


def synth_part(texto, out_path):
    speech_config = speechsdk.SpeechConfig(subscription=KEY, region=REGION)
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio24Khz96KBitRateMonoMp3
    )
    audio_config = speechsdk.audio.AudioOutputConfig(filename=out_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    ssml = (f"<speak version='1.0' xml:lang='es-ES'>"
            f"<voice xml:lang='es-ES' xml:gender='Male' name='{VOZ}'>{esc(texto)}</voice></speak>")
    result = synthesizer.speak_ssml_async(ssml).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise RuntimeError(f"fallo TTS: {result.reason} {getattr(result,'cancellation_details',None)}")


for cap_id in IDS:
    cap = by_id[cap_id]
    out_path = cap["audio"]
    texto = " ".join(cap["oraciones"])
    print(f"{cap_id}: {len(texto)} caracteres -> {out_path}")
    if len(texto) <= MAX_CHARS:
        synth_part(texto, out_path)
    else:
        partes = dividir(texto, MAX_CHARS)
        print(f"  dividido en {len(partes)} partes")
        parciales = []
        for j, parte in enumerate(partes):
            rp = f"{out_path}.part{j}.tmp"
            synth_part(parte, rp)
            parciales.append(rp)
        with open(out_path, "wb") as out:
            for rp in parciales:
                with open(rp, "rb") as fpart:
                    out.write(fpart.read())
                os.remove(rp)
    print(f"  OK ({os.path.getsize(out_path)} bytes)")

print("listo")
