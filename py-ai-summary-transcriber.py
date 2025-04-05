import whisper
import openai
import os
from dotenv import load_dotenv

# ========== CARICA LE CHIAVI DAL .env ==========
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AUDIO_FILE = "sample.mp3"

# ========== 1. TRASCRIZIONE WHISPER ==========
print("📝 Trascrizione in corso...")
model = whisper.load_model("base")
result = model.transcribe(AUDIO_FILE)
transcription = result["text"]
print("\n📄 Trascrizione:\n")
print(transcription)

# ========== 2. RIASSUNTO CON OPENAI ==========
print("\n🧠 Riassunto AI...")

openai.api_key = OPENAI_API_KEY

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Sei un assistente che riassume le call aziendali."},
        {"role": "user", "content": f"Riassumi la seguente conversazione:\n\n{transcription}"}
    ]
)

summary = response.choices[0].message.content

print("\n🟩 RIASSUNTO:\n")
print(summary)

# ========== 3. SALVA I RISULTATI ==========
with open("trascrizione.txt", "w", encoding="utf-8") as f:
    f.write(transcription)

with open("riassunto.txt", "w", encoding="utf-8") as f:
    f.write(summary)
