# faster-whisper-vui
A simple web-UI for faster-whisper.

## Features
- Run a python server which can do these things
- Select a local audio file and upload it to the server.
- Transcribe the audio file to a .srt subtitle file.
- Download the .srt file.

## Needs
- Only tested in Centos. You can run it in Ubuntun or else linux systems.
- Python 3.10
- pytorch
- fastapi
- uvicorn
- faster-whisper
- Module: whisper-large-v3-float32

## Install
- install python-3.10
- pip the requirements
- python main.py

## Config
- modify the config.json to change the server config.
- You can change the "model_path" to indicate the model path.
- "device" : cuda or cpu, depends Nvidia card support.
- "upload_path" : uploaded file directory.
- "output_path" : Transcribed .srt file position.
