# 🎙️ Voice Cloner — Vakya 2.0

A simple local Gradio website for Hindi and other Indian-language voice cloning using **Vakya 2.0**, based on the **IndicF5** architecture.

The app takes a short reference voice clip and generates speech in the cloned voice. Vakya 2.0 supports 11 Indian languages and outputs audio at 24 kHz.

## Source / Credits

The original playground is by **ashishkblink**:
https://huggingface.co/spaces/ashishkblink/vakya-tts-playground

Model:
https://huggingface.co/ashishkblink/vakya2.0

Vakya 2.0 is based on AI4Bharat's IndicF5:
https://github.com/AI4Bharat/IndicF5

Model weights are **not stored in this repository**. They are downloaded from Hugging Face at runtime.

## Setup

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

pip install git+https://github.com/SWivid/F5-TTS.git
pip install -r requirements.txt

Copy-Item .env.example .env
# Edit .env and put your Hugging Face token in HF_TOKEN

python app.py
```

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate

pip install git+https://github.com/SWivid/F5-TTS.git
pip install -r requirements.txt

cp .env.example .env
# Edit .env and put your Hugging Face token in HF_TOKEN

python app.py
```

Then open:

http://localhost:7860

## Usage

1. Click **Load Model**.
2. Upload or record a short reference clip.
3. Optionally enter the words spoken in that reference clip.
4. Enter Hindi or another supported-language text.
5. Click **Generate Speech**.

## Supported languages

Assamese, Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil and Telugu.

## Important

Use voice cloning only with appropriate permission from the speaker. Do not use the project for impersonation, fraud, harassment, or other unauthorized use.

## License / attribution

The source playground identifies Vakya 2.0 as MIT licensed and credits AI4Bharat's IndicF5. See the original model and playground repositories for their current terms.
