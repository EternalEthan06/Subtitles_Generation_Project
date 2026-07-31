from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os

# Import master pipeline
from video_captioning.core.pipeline import process_video

# Create the actual web application
app = FastAPI(title = "AI Subtitles API")

# Tell the server to listen for POST requests at the "/upload" URL
@app.post("/upload")
# 'async' means this function can pause and let other users use the 
# website while it waits for things to finish.
# 'UploadFile = File(...)' is FastAPI magic. It automatically catches 
# the incoming video from the internet and prepares it for us to use.
async def upload_video(video: UploadFile = File(...)):
    print(f"Received video: {video.filename}")

    # 1. Save the uploaded video from the internet onto server's hard drive
    temp_video_path = f"temp_{video.filename}"
    #  We create an empty file on our hard drive. "wb" stands for "Write Binary".
    # (Because videos are binary data, not text).
    with open(temp_video_path, "wb") as buffer:
        # We use shutil to copy the file data securely
        shutil.copyfileobj(video.file, buffer)

        try:
            # 2. Run our AI Pipeline on the saved video
            print("Passing to AI Pipeline...")
            srt_file_path = process_video(temp_video_path)

            # 3. Send the generated .srt file back to the user's browser
            # filename = "..." forces the browser to download it as a file
            return FileResponse(srt_file_path, filename = srt_file_path)

        finally:
            # CLEANUP: Delete the temporary video file we saved in step 1
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)

# A simple welcome endpoint just to check if the server is alive
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Subtitle Generator API!"}