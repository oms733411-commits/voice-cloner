"""
Vakya 2.0 - Text-to-Speech Playground
A local Gradio app for testing the Vakya TTS model.
"""

import os
import sys
import tempfile
from pathlib import Path

import gradio as gr
import numpy as np
import soundfile as sf
import torch
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download, snapshot_download

# Load local environment variables (HF_TOKEN, etc.).
load_dotenv()

# Make local/project imports available.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from f5_tts.api import F5TTS
    from f5_tts.infer.utils_infer import preprocess_ref_audio_text
except ImportError as exc:
    raise ImportError(
        "Could not import f5_tts. Install F5-TTS with: "
        "pip install git+https://github.com/SWivid/F5-TTS.git"
    ) from exc

MODEL_REPO_ID = "ashishkblink/vakya2.0"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
tts_model = None


def load_model():
    """Load the Vakya model from Hugging Face."""
    global tts_model

    if tts_model is not None:
        return "✅ Model already loaded!"

    print("Loading Vakya model...")
    print(f"Device: {DEVICE}")

    try:
        print(f"Downloading model files from Hugging Face: {MODEL_REPO_ID}")
        token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")

        if token:
            try:
                from huggingface_hub import login
                login(token=token, add_to_git_credential=False)
            except Exception:
                pass

        model_dir = snapshot_download(
            repo_id=MODEL_REPO_ID,
            cache_dir=None,
            local_files_only=False,
            token=token,
        )

        model_dir_path = Path(model_dir)
        ckpt_files = list(model_dir_path.rglob("*.safetensors")) + list(
            model_dir_path.rglob("*.pt")
        )
        vocab_files = list(model_dir_path.rglob("vocab.txt"))

        ckpt_file = str(ckpt_files[0]) if ckpt_files else ""
        vocab_file = str(vocab_files[0]) if vocab_files else ""

        if not ckpt_file:
            try:
                ckpt_file = hf_hub_download(
                    repo_id=MODEL_REPO_ID,
                    filename="model.safetensors",
                    cache_dir=None,
                    token=token,
                )
            except Exception:
                try:
                    ckpt_file = hf_hub_download(
                        repo_id=MODEL_REPO_ID,
                        filename="pytorch_model.bin",
                        cache_dir=None,
                        token=token,
                    )
                except Exception:
                    pass

        if not vocab_file:
            try:
                vocab_file = hf_hub_download(
                    repo_id=MODEL_REPO_ID,
                    filename="vocab.txt",
                    cache_dir=None,
                    token=token,
                )
            except Exception:
                pass

        tts_model = F5TTS(
            model_type="F5-TTS",
            ckpt_file=ckpt_file if ckpt_file else "",
            vocab_file=vocab_file if vocab_file else "",
            device=DEVICE,
            vocoder_name="vocos",
        )

        print("✅ Model loaded successfully!")
        return "✅ Model loaded successfully!"

    except Exception as exc:
        error_msg = str(exc)
        print(f"❌ Error loading model: {error_msg}")

        if (
            "401" in error_msg
            or "Repository Not Found" in error_msg
            or "Invalid username or password" in error_msg
        ):
            return (
                f"❌ Authentication Error: '{MODEL_REPO_ID}' may require a Hugging Face "
                "token. Put your token in HF_TOKEN in .env."
            )

        import traceback
        traceback.print_exc()
        return f"❌ Error loading model: {error_msg}"


def generate_speech(ref_audio, ref_text, gen_text, speed, remove_silence):
    """Generate speech from text using reference audio."""
    global tts_model

    if tts_model is None:
        return None, "⚠️ Please load the model first by clicking 'Load Model'."

    if ref_audio is None:
        return None, "⚠️ Please upload a reference audio file."

    if not gen_text or not gen_text.strip():
        return None, "⚠️ Please enter text to generate."

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_ref:
            if isinstance(ref_audio, tuple):
                sr, audio_data = ref_audio
                sf.write(tmp_ref.name, audio_data, sr)
                ref_audio_path = tmp_ref.name
            elif isinstance(ref_audio, str):
                ref_audio_path = ref_audio
            else:
                return None, "⚠️ Invalid audio format."

        ref_audio_processed, ref_text_processed = preprocess_ref_audio_text(
            ref_audio_path,
            ref_text if ref_text else "",
            device=DEVICE,
        )

        print(f"Generating speech for: {gen_text[:50]}...")

        wav, sr, _ = tts_model.infer(
            ref_file=ref_audio_processed,
            ref_text=ref_text_processed,
            gen_text=gen_text,
            speed=speed,
            remove_silence=remove_silence,
            show_info=print,
            progress=None,
        )

        if isinstance(wav, torch.Tensor):
            wav = wav.cpu().numpy()

        if len(wav.shape) > 1:
            wav = wav.squeeze()

        if wav.dtype == np.int16:
            wav = wav.astype(np.float32) / 32768.0
        elif wav.size and wav.max() > 1.0:
            wav = wav / np.abs(wav).max()

        return (sr, wav), f"✅ Generated {len(wav) / sr:.2f} seconds of audio"

    except Exception as exc:
        error_msg = f"❌ Error generating speech: {exc}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return None, error_msg


with gr.Blocks(
    title="Vakya 2.0 - Text-to-Speech",
    theme=gr.themes.Soft(),
) as app:
    gr.Markdown(
        """
# 🎙️ Vakya 2.0 - Text-to-Speech Playground

**Vakya** supports 11 Indian languages: Assamese, Bengali, Gujarati, Hindi,
Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu.

### How to use
1. Click **Load Model**.
2. Upload a short reference audio clip (<15 seconds recommended).
3. Enter reference text if known (optional).
4. Enter the text to generate.
5. Adjust speed/settings if needed.
6. Click **Generate Speech**.
"""
    )

    with gr.Row():
        with gr.Column():
            load_btn = gr.Button("🚀 Load Model", variant="primary", size="lg")
            model_status = gr.Textbox(
                label="Model Status",
                value="⏳ Model not loaded",
                interactive=False,
            )

        load_btn.click(fn=load_model, outputs=model_status)

    with gr.Row():
        with gr.Column():
            ref_audio_input = gr.Audio(
                label="Reference Audio",
                type="numpy",
                sources=["upload", "microphone"],
                format="wav",
            )
            ref_text_input = gr.Textbox(
                label="Reference Text (Optional)",
                placeholder="Enter the text spoken in the reference audio.",
                lines=3,
                info="Leave blank for automatic transcription when supported.",
            )

        with gr.Column():
            gen_text_input = gr.Textbox(
                label="Text to Generate",
                placeholder="Enter text in any supported Indian language...",
                lines=5,
                info="Supports Assamese, Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil and Telugu.",
            )

    with gr.Accordion("⚙️ Advanced Settings", open=False):
        speed_slider = gr.Slider(
            label="Speed",
            minimum=0.5,
            maximum=2.0,
            value=1.0,
            step=0.1,
            info="Adjust the speed of generated speech.",
        )
        remove_silence = gr.Checkbox(
            label="Remove Silences",
            value=False,
            info="Experimental.",
        )

    generate_btn = gr.Button("🎵 Generate Speech", variant="primary", size="lg")

    with gr.Row():
        audio_output = gr.Audio(label="Generated Audio", type="numpy", autoplay=True)
        status_output = gr.Textbox(label="Status", interactive=False)

    generate_btn.click(
        fn=generate_speech,
        inputs=[
            ref_audio_input,
            ref_text_input,
            gen_text_input,
            speed_slider,
            remove_silence,
        ],
        outputs=[audio_output, status_output],
    )

    gr.Markdown(
        """
---
### 📚 Model Information
- **Model:** Vakya 2.0
- **Repository:** [ashishkblink/vakya2.0](https://huggingface.co/ashishkblink/vakya2.0)
- **Based on:** [IndicF5](https://github.com/AI4Bharat/IndicF5) by AI4Bharat (IIT Madras)
- **Sample rate:** 24000 Hz
- **License:** MIT

### ⚠️ Terms of Use
Only clone voices when you have explicit permission to do so.
"""
    )


if __name__ == "__main__":
    app.queue().launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
    )
