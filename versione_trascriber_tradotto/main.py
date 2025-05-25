import threading
import queue
import time
import os

import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc

import pyaudio
from googletrans import Translator
from faster_whisper import WhisperModel  # pip install faster-whisper

OUTPUT_FILE = "traduzioni_live.txt"

# Setup Open source Whisper (faster-whisper)
model_size = "small"  # puoi mettere tiny, base, small, medium, large
model = WhisperModel(model_size, device="cpu")  # o "cuda" se hai GPU

translator = Translator()

# Audio config
RATE = 16000
CHUNK = 1024

# Queue per audio streaming
audio_queue = queue.Queue()
text_queue = queue.Queue()

running = False
audio_source = None  # "mic" o "system"

# Funzione per registrazione audio da device specifico
def audio_capture(device_index):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
                    frames_per_buffer=CHUNK, input_device_index=device_index)
    while running:
        data = stream.read(CHUNK)
        audio_queue.put(data)
    stream.stop_stream()
    stream.close()
    p.terminate()

# Funzione di trascrizione streaming
def transcribe_loop():
    global running
    buffer = b""
    segment_duration = 5  # secondi, buffer minimo per trascrivere
    segment_frames = RATE * segment_duration * 2  # 2 byte per sample

    while running:
        try:
            data = audio_queue.get(timeout=1)
            buffer += data

            if len(buffer) >= segment_frames:
                audio_data = buffer[:segment_frames]
                buffer = buffer[segment_frames:]

                # Decodifica audio e trascrivi
                segments, _ = model.transcribe(audio_data, beam_size=5)
                for segment in segments:
                    text = segment.text.strip()
                    if text:
                        translated = translator.translate(text, dest="it").text
                        text_queue.put((text, translated))
                        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                            f.write(f"Originale: {text}\nTradotto: {translated}\n\n")
        except queue.Empty:
            continue

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2("Traduzione Live Audio Microfono / Audio di Sistema"),
    dbc.RadioItems(
        id="audio-source",
        options=[
            {"label": "Microfono", "value": "mic"},
            {"label": "Audio di Sistema", "value": "system"}
        ],
        value="mic",
        inline=True,
        style={"marginBottom": "15px"}
    ),
    dbc.Button("Avvia Traduzione", id="start-btn", color="primary", className="me-2"),
    dbc.Button("Ferma Traduzione", id="stop-btn", color="danger"),
    html.Hr(),
    html.Div(id="output-text", style={"whiteSpace": "pre-line", "height": "300px", "overflowY": "scroll", "border": "1px solid #ccc", "padding": "10px"}),
    dcc.Interval(id="update-interval", interval=1000, disabled=True)
])

# Trova device index per microfono o audio sistema (qui dev'essere adattato manualmente)
def find_audio_device(name_hint):
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if name_hint.lower() in dev["name"].lower() and dev["maxInputChannels"] > 0:
            p.terminate()
            return i
    p.terminate()
    return None

threads = []

@app.callback(
    Output("update-interval", "disabled"),
    Output("output-text", "children"),
    Input("start-btn", "n_clicks"),
    Input("stop-btn", "n_clicks"),
    State("audio-source", "value"),
    State("output-text", "children"),
    prevent_initial_call=True
)
def control_translation(start_clicks, stop_clicks, source, current_text):
    global running, audio_source, threads
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "start-btn":
        if running:
            return dash.no_update, dash.no_update

        running = True
        audio_source = source
        # Reset output text
        current_text = ""

        # Scegli device audio
        if audio_source == "mic":
            device_index = find_audio_device("microphone") or 0
        else:
            # Devi indicare il nome del device virtuale o mix di sistema
            device_index = find_audio_device("stereo mix") or 0

        # Avvia thread registrazione e trascrizione
        threads = [
            threading.Thread(target=audio_capture, args=(device_index,), daemon=True),
            threading.Thread(target=transcribe_loop, daemon=True)
        ]
        for t in threads:
            t.start()

        return False, current_text

    elif button_id == "stop-btn":
        running = False
        # Aspetta che i thread finiscano
        for t in threads:
            t.join(timeout=1)
        return True, current_text

    return dash.no_update, dash.no_update

@app.callback(
    Output("output-text", "children"),
    Input("update-interval", "n_intervals"),
    State("output-text", "children")
)
def update_output(n, current_text):
    new_texts = []
    while not text_queue.empty():
        orig, trad = text_queue.get()
        new_texts.append(f"Originale: {orig}\nTradotto: {trad}\n")

    if new_texts:
        return current_text + "\n".join(new_texts)
    return current_text

if __name__ == "__main__":
    app.run_server(debug=True)
