# Video Automation Machine - Web UI
"""FastAPI web interface for the Video Automation Machine.

Run with:
    python -m ui.web
    or
    uvicorn ui.web:app --reload
"""

import os
import asyncio
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.types import VideoOutput
from core.factory import create_engine_from_env
from core.logging_utils import setup_logger


logger = setup_logger("vam.web")
app = FastAPI(title="Video Automation Machine", version="1.0.0")

# Templates directory
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)

# Static files directory
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates
templates = Jinja2Templates(directory=str(templates_dir))


# Simple inline HTML template (no external dependencies)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Automation Machine</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        textarea { min-height: 100px; font-family: monospace; }
        select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button {
            background: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #0056b3; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .result {
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .result h3 { margin-top: 0; color: #28a745; }
        .log {
            font-family: monospace;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            max-height: 300px;
            overflow-y: auto;
            margin: 10px 0;
        }
        .error { color: #dc3545; }
        .status { font-weight: bold; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <h1>🎬 Video Automation Machine</h1>
    <p>Generate short vertical videos from prompts or scripts</p>
    
    <div class="form-group">
        <label for="prompt">Prompt (video topic)</label>
        <textarea id="prompt" name="prompt" placeholder="e.g., A beautiful sunset over the ocean..."></textarea>
    </div>
    
    <div class="form-group">
        <label for="script_file">Or upload a script file</label>
        <input type="file" id="script_file" name="script_file" accept=".txt">
    </div>
    
    <div class="form-group">
        <label>Provider Options (defaults shown)</label>
        <select disabled title="Provider options are configured via .env file">
            <option selected>LLM: Default (OpenAI-compatible)</option>
        </select>
        <select disabled title="Provider options are configured via .env file">
            <option selected>Video: Pexels</option>
        </select>
        <select disabled title="Provider options are configured via .env file">
            <option selected>TTS: Edge-TTS (Free)</option>
        </select>
    </div>
    
    <button id="generate_btn" onclick="generateVideo()">Generate Video</button>
    
    <div id="result" class="result hidden">
        <h3>Result</h3>
        <div id="status" class="status"></div>
        <div id="log" class="log"></div>
        <div id="output" class="hidden">
            <p><strong>Output Path:</strong> <code id="output_path"></code></p>
            <p><strong>Duration:</strong> <span id="duration"></span></p>
            <p><strong>Resolution:</strong> <span id="resolution"></span></p>
            <p><strong>Segments:</strong> <span id="segments"></span></p>
        </div>
    </div>
    
    <script>
        async function generateVideo() {
            const prompt = document.getElementById('prompt').value.trim();
            const scriptFile = document.getElementById('script_file').files[0];
            
            if (!prompt && !scriptFile) {
                alert('Please provide either a prompt or upload a script file');
                return;
            }
            
            const btn = document.getElementById('generate_btn');
            const resultDiv = document.getElementById('result');
            const logDiv = document.getElementById('log');
            
            btn.disabled = true;
            btn.textContent = 'Generating...';
            resultDiv.classList.remove('hidden');
            logDiv.innerHTML = '<p>[INIT] Starting video generation...</p>';
            
            const formData = new FormData();
            if (prompt) formData.append('prompt', prompt);
            if (scriptFile) formData.append('script_file', scriptFile);
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    logDiv.innerHTML += '<p><strong>[SUCCESS] Video generated!</strong></p>';
                    document.getElementById('output_path').textContent = data.output_path;
                    document.getElementById('duration').textContent = data.duration + 's';
                    document.getElementById('resolution').textContent = data.width + 'x' + data.height;
                    document.getElementById('segments').textContent = data.segments_count;
                    document.getElementById('output').classList.remove('hidden');
                } else {
                    logDiv.innerHTML += '<p class="error"><strong>[ERROR] ' + (data.message || 'Unknown error') + '</strong></p>';
                }
                
            } catch (error) {
                logDiv.innerHTML += '<p class="error"><strong>[ERROR] ' + error.message + '</strong></p>';
            } finally {
                btn.disabled = false;
                btn.textContent = 'Generate Video';
            }
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main HTML page."""
    return HTMLResponse(content=HTML_TEMPLATE)


@app.post("/api/generate")
async def generate(
    request: Request,
    prompt: Optional[str] = Form(None),
    script_file: Optional[UploadFile] = File(None)
):
    """Generate a video from prompt or script file.
    
    Args:
        request: FastAPI request object
        prompt: Optional text prompt for video topic
        script_file: Optional uploaded script file
        
    Returns:
        JSON response with status, output path, and video info
    """
    logger.info("[WEB] Received generate request")
    
    # Validate input
    if not prompt and not script_file:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Either prompt or script_file must be provided"}
        )
    
    try:
        # Load engine
        logger.info("[WEB] Creating engine...")
        engine = create_engine_from_env()
        
        # Process based on input type
        if script_file:
            # Read uploaded script file
            content = await script_file.read()
            script_text = content.decode('utf-8')
            logger.info(f"[WEB] Processing script file: {script_file.filename}")
            video_output = await engine.run_from_script(script_text)
        else:
            logger.info(f"[WEB] Processing prompt: {prompt[:50]}...")
            video_output = await engine.run_from_prompt(prompt)
        
        logger.info(f"[WEB] Video generated: {video_output.output_path}")
        
        return JSONResponse(content={
            "status": "success",
            "output_path": video_output.output_path,
            "duration": video_output.duration,
            "width": video_output.width,
            "height": video_output.height,
            "file_size": video_output.file_size,
            "segments_count": video_output.segments_count,
            "audio_provider": video_output.audio_provider,
            "video_provider": video_output.video_provider
        })
        
    except Exception as e:
        logger.error(f"[WEB] Error generating video: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the FastAPI server."""
    import uvicorn
    uvicorn.run(
        "ui.web:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Start the Video Automation Machine web UI")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    
    args = parser.parse_args()
    
    logger.info(f"[WEB] Starting web server at http://{args.host}:{args.port}")
    logger.info("[WEB] Press Ctrl+C to stop")
    run_server(args.host, args.port)
