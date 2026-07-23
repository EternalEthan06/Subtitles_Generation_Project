import whisper
import torch

def transcribe_audio(audio_path: str, model_size: str = "base"):
    """
    Loads a Whisper model and transcribes the provided audio file.
    Returns a list of 'segments' (dictionaries containing the text and timestamps).
    """
    print(f"Loading Whisper '{model_size}' model...")

    # Whisper can run on a CPU but much faster on a GPU
    # Checks if there is a compatible NVIDIA GPU (CUDA).
    # If not, fall back to use CPU.
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load the model into memory.
    # Note: The very first time it runs this, it will download the model file from the Internet
    model = whisper.load_model(model_size, device=device)

    print(f"Transcribing {audio_path} (this might take a minute)...")

    # This is where the AI actually listens to the audio and generates text.
    # Set fp16=False to avoid warnings if it is running on a CPU.
    result = model.transcribe(audio_path, fp16=False)

    # 'result' is a bid dictionary. The 'segments' key holds exactly what we need:
    # A list of sentences, each with a 'start' and 'end' timestamp in seconds.
    segments = result['segments']

    print(f"Success! Extracted {len(segments)} segments of text.")
    return segments

# --- Testing Block ---
if __name__ == "__main__":
    test_audio = "../../preprocessing/extracted_audio.wav"

    try:
        segments = transcribe_audio(test_audio)

        # Print out the first 3 segments to see what the AI gave us
        print("\n--- Preview of Transcription ---")
        for i, segment in enumerate(segments[:3]):
            start = round(segment['start'], 2)
            end = round(segment['end'], 2)
            text = segment['text']
            print(f"[{start}s -> {end}s]: {text}")
        
    except FileNotFoundError:
        print("Test audio file not found! Make sure you ran the audio.py test first.")