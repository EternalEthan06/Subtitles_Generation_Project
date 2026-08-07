import os

# import 3 functions built in the previous steps
from video_captioning.preprocessing.audio import extract_audio
from video_captioning.models.transcriber import transcribe_audio
from video_captioning.postprocessing.subtitle_generator import generate_srt

def process_video(video_path: str):
    """
    The master pipeline: Video -> Audio -> Text -> Subtitles.
    """

    print(f"--- Starting Pipeline for: {video_path} ---")

    # 1. Setup file paths based on the video name
    # If video is "my_video.mp4", this creates "my_video.wav" and "my_video.srt"
    base_name = os.path.splitext(video_path)[0]
    temp_audio_path = f"{base_name}.wav"
    output_srt_path = f"{base_name}.srt"

    try:
        # Step 1: Extract Audio
        print("\n[Step 1/3] Extracting Audio...")
        extract_audio(video_path, temp_audio_path)

        # Step 2: Transcribe
        print("\n[Step 2/3] Transcribing Audio...")
        # (We'll use the 'base' model to keep things fast for testing)
        segments = transcribe_audio(temp_audio_path, model_size = "base")

        # Step 3: Generate Subtitles
        print("\nStep [3/3 Generating Subtitles File...]")
        generate_srt(segments, output_srt_path)

        print(f"\n--- Pipeline Complete! Your subtitles are ready at: {output_srt_path} ---")

        return output_srt_path
    
    finally:
        # CLEANUP: Delete the temporary .wav file do we don't clog up the hard drive
        if os.path.exists(temp_audio_path):
            print(f"Cleaning up temporary audio file: {temp_audio_path}")
            os.remove(temp_audio_path)

# --- Testing Block ---
if __name__ == "__main__":
    # Point this to a REAL video file your computer to test the whole system
    # Make sure to use forward slashes (/) or double backslashes (\\) in the path.
    my_video = "../../test_video.mp4"

    if os.path.exists(my_video):
        process_video(my_video)
    else:
        print(f"Please put a video file named {my_video} in the correct folder to test the pipeline!")
