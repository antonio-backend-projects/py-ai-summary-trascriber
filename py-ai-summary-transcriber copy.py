import whisper
from pyannote.audio import Pipeline
import openai
import os
from dotenv import load_dotenv

# ========== CARICA LE CHIAVI DAL .env ==========
load_dotenv()  # Carica il file .env

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AUDIO_FILE = "sample.mp3"

# ========== 1. DIARIZZAZIONE (CHI PARLA E QUANDO) ==========
print("🗣️ Identificazione dei parlanti...")
pipeline = Pipeline.from_pretrained("pyannote/segmentation", use_auth_token=HUGGINGFACE_TOKEN)
diarization = pipeline(AUDIO_FILE)

segments = []
for turn, _, speaker in diarization.itertracks(yield_label=True):
    segments.append({
        "start": turn.start,
        "end": turn.end,
        "speaker": speaker
    })

# ========== 2. TRASCRIZIONE WHISPER ==========
print("📝 Trascrizione in corso...")
model = whisper.load_model("base")
whisper_result = model.transcribe(AUDIO_FILE, word_timestamps=True)

words = whisper_result["segments"]

# ========== 3. COMBINAZIONE ==========
print("🔗 Combinazione trascrizione + parlanti...")

def match_words_to_speakers(segments, words):
    combined = []
    for segment in segments:
        start, end, speaker = segment["start"], segment["end"], segment["speaker"]
        speaker_words = []
        for whisper_segment in words:
            if whisper_segment['start'] >= start and whisper_segment['end'] <= end:
                speaker_words.append(whisper_segment['text'])
        if speaker_words:
            combined.append(f"{speaker}: {' '.join(speaker_words)}")
    return combined

conversation = match_words_to_speakers(segments, words)
full_transcript = "\n".join(conversation)
print(full_transcript)

# ========== 4. RIASSUNTO CON OPENAI ==========
print("🧠 Riassunto AI...")

openai.api_key = OPENAI_API_KEY

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Sei un assistente che riassume le call aziendali."},
        {"role": "user", "content": f"Riassumi la seguente conversazione:\n\n{full_transcript}"}
    ]
)

summary = response.choices[0].message.content

print("\n🟩 RIASSUNTO:\n")
print(summary)

# ========== (Opzionale) Salva i risultati ==========
with open("trascrizione.txt", "w", encoding="utf-8") as f:
    f.write(full_transcript)

with open("riassunto.txt", "w", encoding="utf-8") as f:
    f.write(summary)
