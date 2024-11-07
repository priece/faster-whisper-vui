import logging
import json
import shutil
import os
from faster_whisper import WhisperModel
from datetime import datetime

class FasterWhisperService:
    def __init__(self, config_file_path="config.json"):
        self.config_file_path = config_file_path
        # logging config
        logging.basicConfig()
        logging.getLogger("faster_whisper").setLevel(logging.DEBUG)
        print("FasterWhisperService: load config file begin")
        
        with open(config_file_path, 'r', encoding='utf-8') as file:
            config = json.load(file)

        print(config)
        self.config = config
        self.model=None
    
    def load_model(self):
        print("load_model begin")
        model_path = self.config["model_path"]
        compute_type = self.config["compute_type"]
        device = self.config["device"]
        model = WhisperModel(model_size_or_path=model_path, device=device, compute_type=compute_type, local_files_only=True)  # 使用 GPU 加速

        # reset mel_filters to fix error
        model.feature_extractor.mel_filters = model.feature_extractor.get_mel_filters(
            model.feature_extractor.sampling_rate, 
            model.feature_extractor.n_fft, 
            n_mels=128
        )
        self.model=model
        print("load_model end")
        
    def transcribe(self, audio_file_name):
        audio_file_path = os.path.join(self.config["upload_path"], audio_file_name)
        segments, info = self.model.transcribe(audio_file_path, vad_filter=True, vad_parameters={"min_silence_duration_ms": 500}, beam_size=5)

        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

        now = datetime.now()
        unix_timestamp_ms = int(now.timestamp() * 1000) + now.microsecond // 1000
        
        output_path = self.config["output_path"]
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        srt_file_name = f"{unix_timestamp_ms}.srt"
        srt_file_path = os.path.join(output_path, srt_file_name)
        with open(srt_file_path, "w", encoding="utf-8") as srt_file:
            for i, segment in enumerate(segments, start=1):
                start_time = segment.start
                end_time = segment.end
                
                start_hours = int(start_time // 3600)
                start_minutes = int((start_time % 3600) // 60)
                start_seconds = int(start_time % 60)
                start_ms = int((start_time % 1) * 1000)
                
                end_hours = int(end_time // 3600)
                end_minutes = int((end_time % 3600) // 60)
                end_seconds = int(end_time % 60)
                end_ms = int((end_time % 1) * 1000)

                srt_file.write(f"{i}\n")
                srt_file.write(f"{start_hours:02d}:{start_minutes:02d}:{start_seconds:02d},{start_ms:03d} --> {end_hours:02d}:{end_minutes:02d}:{end_seconds:02d},{end_ms:03d}\n")
                srt_file.write(f"{segment.text}\n\n")
                print(f"{segment.text}\n")
        print(f"SRT subtitles saved to {srt_file_path}")
        return srt_file_name

    def upload_file(self, file):
        now = datetime.now()
        unix_timestamp_ms = int(now.timestamp() * 1000) + now.microsecond // 1000
        filename = f"{unix_timestamp_ms}"

        upload_path = self.config["upload_path"]
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        
        file_path = os.path.join(upload_path , filename)

        with open(file_path, "wb") as buffer:  
            shutil.copyfileobj(file.file, buffer)

        return filename
