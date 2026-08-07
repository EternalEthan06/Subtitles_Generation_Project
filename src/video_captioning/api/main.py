from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
import shutil
import os
import time

# Import master pipeline
from video_captioning.core.pipeline import process_video

# Instantiate the FastAPI web application with metadata for documentation (/docs)
app = FastAPI(
    title = "AI Subtitle Generator",
    description = "Upload video files to generate accurate SRT subtitles powered by OpenAI Whisper.",
    version = "1.0.0"
)

# Define the single-page web UI (HTML, CSS, and JavaScript) to serve to browser visitors
HTML_UI_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset = "UTF-8">
    <meta name = "viewport" content = "width = device-width, initial-scale = 1.0">
    <title>AI Subtitle Gneerator</title>
    <style>
    /* Modern Glassmorphism & Responsive Web Design */
    :root {
        -- primary: #6366f1;
        -- primary-hover: #4f46e5;
        -- bg-dark: #0f172a;
        -- card-bg: rgba(30, 41, 59, 0.7);
        -- text-light: #f8fafc;
        -- text-muted: #94a3b8;
        }

    body {
        font-family: 'Sergoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: var(--bg-dark);
        color: var(--text-light);
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        }
    
    .container {
        background: var(--card-bg);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2.5rem;
        max_width: 550px;
        width: 90%;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        text-align: center;
        }
    
    h1 {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(to right, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        }
    
    p {
        color: var(--text-muted);
        margin-bottom: 2rem;
        }
    
    /* Drag and Drop Zone */
    .drop-zone {
        border: 2px dashed var(--primary);
        border-radius: 12px;
        padding: 3rem 1.5rem;
        cursor: pointer;
        transition: all 0.3 ease;
        background: rgba(99, 102, 241, 0.05);
        }
    
    .drop-zone: hover, .drop-zone.dragover {
        background: rgba(99, 102, 241, 0.15);
        border-color: #a5b4fc;
        }
    
    .drop-zone p {
        margin: 0;
        font-weight: 500;
        }
    
    input[type = "file] {
        display = none;
        }
    
    /* Processing Indicator & Buttons */
    .btn {
        background: var(--primary);
        color: white;
        border: none;
        padding: 0.85rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
        cursor: pointer;
        margin-top: 1.5rem;
        width: 100%;
        transition: background 0.2s ease;
        }

        .btn:hover {
            background: var(--primary-hover);
            }
        
        .btn: disabled {
            opacity: 0.5;
            cursor: not-allowed;
            }

        .status {
            margin-top: 1.5rem;
            font-weight: 500;
            font-size: 0.95rem;
            }

        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, .3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            }
        
        @keyframes spin {
            to {
                transform: rotate(360deg);
                }
            }
        </style>
    </head>
    <body>

    <div class = "container">
        <h1>🎬 AI Subtitle Generator</h1>
        <p>Upload your video (.mp4, .mkv, .mov) to generate AI subtitles instantly.</p>

        <!--- File Selection Box --->
        <div class = "drop-zone" 
        id = "dropZone" 
        onclick = "document.getElementById('videoInput').click()">
            <p id = "fileName">📁 Click or Drag & Drop Video Here</p>
            <input type = "file"
            id  = "videoInput"
            accept = "video/*"
            onchange="handleFileSelect(event)">
    </div>
    <button class="btn" id="uploadBtn" onclick="uploadVideo()" disabled>Generate SRT Subtitles</button>
    <!-- Status Message Display -->
    <div class="status" id="statusMsg"></div>
</div>
<script>
    let selectedFile = null;
    // Triggered when user selects a file via file picker
    function handleFileSelect(event) {
        selectedFile = event.target.files[0];
        if (selectedFile) {
            document.getElementById('fileName').innerText = '🎥 Selected: ' + selectedFile.name;
            document.getElementById('uploadBtn').disabled = false;
        }
    }
    // Drag and Drop Event Listeners
    const dropZone = document.getElementById('dropZone');
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            selectedFile = e.dataTransfer.files[0];
            document.getElementById('fileName').innerText = '🎥 Selected: ' + selectedFile.name;
            document.getElementById('uploadBtn').disabled = false;
        }
    });
    // Upload Video to FastAPI /upload endpoint via AJAX fetch()
    async function uploadVideo() {
        if (!selectedFile) return;
        const uploadBtn = document.getElementById('uploadBtn');
        const statusMsg = document.getElementById('statusMsg');
        // Disable UI and show loading spinner
        uploadBtn.disabled = true;
        statusMsg.innerHTML = '<span class="spinner"></span> Extracting Audio & Transcribing AI Subtitles... (This may take a minute)';
        // Prepare multipart form data payload
        const formData = new FormData();
        formData.append('video', selectedFile);
        try {
            // POST request to FastAPI endpoint
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            if (!response.ok) {
                throw new Error('Server returned error status: ' + response.status);
            }
            // Convert server file response into a browser downloadable blob
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = selectedFile.name.split('.')[0] + '.srt';
            document.body.appendChild(a);
            a.click();
            a.remove();
            statusMsg.innerHTML = '✅ <strong>Success!</strong> Subtitle downloaded automatically.';
        } catch (error) {
            console.error(error);
            statusMsg.innerHTML = '❌ <strong>Error:</strong> Failed to generate subtitles. Check server logs.';
        } finally {
            uploadBtn.disabled = false;
        }
    }
</script>
</body>
</html>
"""

@app.get("/", response_class = HTMLResponse)
def serve_frontend():
    """
    Renders the web frontend interactive interface.
    Returns HTMLResponse containing the single-page application UI.
    """
    return HTML_UI_CONTENT


# Tell the server to listen for POST requests at the "/upload" URL
# The "@" symbol is called a "Decorator". 
# It acts like a traffic cop. It tells the server: "If anyone on the 
# internet sends data (POST) to ourwebsite.com/upload, send them to the function below!"
@app.post("/upload")
# 'async' means this function can pause and let other users use the 
# website while it waits for things to finish.
# 'UploadFile = File(...)' is FastAPI magic. It automatically catches 
# the incoming video from the internet and prepares it for us to use.
async def upload_video(video: UploadFile = File(...)):
    """
    Asynchronous file receiver endpoint.

    Parameters:
        video (UploadFile): Incoming video stream received via HTTP multipart/form-data.
    
    Returns:
        FileResponse: Returns generated .srt subtitle file for browser download.
    """

    print(f"\n[API Request] Received video upload: {video.filename}")

    # 1. Save the uploaded video from the internet onto server's hard drive
    timestamp = int(time.time())
    temp_video_path = f"temp_{timestamp}_{video.filename}"

    try:
        #  We create an empty file on our hard drive. "wb" stands for "Write Binary".
        # (Because videos are binary data, not text).
        with open(temp_video_path, "wb") as buffer:
            # We use shutil to copy the file data securely
            shutil.copyfileobj(video.file, buffer)

            # 2. Run our AI Pipeline on the saved video
            print(f"[API Request] Video saved temporarily to disk: {temp_video_path}")
            srt_file_path = process_video(temp_video_path)

            # Verify subtitle generation output
            if not os.path.exists(srt_file_path):
                raise HTTPException(status_code = 500, detail = "Pipeline failed to produce output SRT file.")

            # 3. Send the generated .srt file back to the user's browser
            # filename = "..." forces the browser to download it as a file
            output_filename = f"{os.path.splitext(video.filename)[0]}.srt"
            return FileResponse(path=srt_file_path, media_type="text/plain", filename = output_filename)

    except Exception as err:
        print(f"[API Error] Processing failed: {err}")
        raise HTTPException(status_code = 500, detail = f"Processing failed: {str(err)}")

    finally:
        # CLEANUP: Delete the temporary video file we saved in step 1
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
