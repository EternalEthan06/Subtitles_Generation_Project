import ffmpeg
import os

def extract_audio(video_path: str, output_audio_path: str) -> str:
    """
    Extracts audio from a video file and saves it as a .wav file.
    """
    # Checks if the file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Oops! Could not find the video at: {video_path}")
    
    print(f"Extracting audio from {video_path}...")

    try:
        # Use ffmpeg to read the input video
        stream = ffmpeg.input(video_path)

        # Tell ffmpeg that we want to output audio
        # ac=1 means 1 audio channel (mono), ar = '16k' means 16kHz sample rate.
        # Whisper (AI model) works best with 16kHz mono audio
        stream = ffmpeg.output(stream, output_audio_path, ac=1, ar='16k')

        # 'overwrite_output()' ensures we don't get an error if the .wav fiel already exists.
        # 'run(quiet=True)' executes the command without flooding the terminal with logs.

        ffmpeg.run(ffmpeg.overwrite_output(stream), quiet=True)

        print(f"Success! Audio saved to {output_audio_path}")
        return output_audio_path
    
    except ffmpeg.Error as e:
        # If ffmpeg crashes, this will catch the error so the whole app doesn't break
        print("An error occurred during audio extraction.")
        raise e