## 📝 py-ai-summary-transcriber

Uno script Python per:
1. Trascrivere file audio utilizzando [OpenAI Whisper](https://github.com/openai/whisper)
2. Riassumere automaticamente la conversazione tramite l'API OpenAI (ChatGPT)

> 🎯 Ideale per trascrivere e riassumere call aziendali, meeting o note vocali.

---

### 📁 Struttura del progetto

```
py-ai-summary-transcriber/
├── sample.mp3              # File audio di esempio da trascrivere
├── py-ai-summary-transcriber.py  # Script principale
├── .env                    # Contiene le chiavi API
├── trascrizione.txt        # Output: trascrizione completa
├── riassunto.txt           # Output: riassunto AI
└── README.md               # Questo file
```

---

### ⚙️ Requisiti

- Python 3.9 o superiore
- Librerie Python:
  - `openai==0.28`
  - `openai-whisper`
  - `python-dotenv`

---

### 🚀 Installazione

1. **Clona il repository**
   ```bash
   git clone https://github.com/tuo-username/py-ai-summary-transcriber.git
   cd py-ai-summary-transcriber
   ```

2. **Installa le dipendenze**
   Si consiglia l'uso di un ambiente virtuale:

   ```bash
   python -m venv venv
   source venv/bin/activate   # oppure venv\Scripts\activate su Windows
   ```

   Poi installa i pacchetti necessari:
   ```bash
   pip install openai==0.28 openai-whisper python-dotenv
   ```

3. **Crea il file `.env`**
   Nella root del progetto, crea un file `.env` contenente la tua API key di OpenAI:

   ```
   OPENAI_API_KEY=la_tua_chiave_openai
   ```

4. **Inserisci il file audio**
   Sostituisci `sample.mp3` con il tuo file audio. Può essere `.mp3`, `.wav`, `.m4a`, ecc.

---

### ▶️ Esecuzione

Esegui lo script principale:

```bash
python py-ai-summary-transcriber.py
```

Lo script farà tre cose:

1. Trascriverà l’audio con Whisper
2. Genererà un riassunto con GPT-4 (via API OpenAI)
3. Salverà i risultati in due file:
   - `trascrizione.txt`
   - `riassunto.txt`

---

### 📌 Note

- Assicurati che il file audio non sia troppo lungo, per evitare timeout con Whisper o limiti di token con l’API di OpenAI.
- Puoi cambiare il modello Whisper da `"base"` a `"small"`, `"medium"` o `"large"` per maggiore precisione (ma più tempo e memoria).

---

### 📦 Versioni consigliate

| Pacchetto       | Versione     |
|-----------------|--------------|
| Python          | >= 3.9       |
| `openai`        | `0.28`       |
| `openai-whisper`| Ultima       |
| `python-dotenv` | Ultima       |

---

### 📥 To-do futuri

- [ ] Aggiungere riconoscimento dei parlanti (speaker diarization)
- [ ] GUI desktop (Tkinter)
- [ ] Interfaccia web (Streamlit o FastAPI)
- [ ] Supporto multi-lingua

