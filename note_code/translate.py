import os
import whisper
from googletrans import Translator
from datetime import timedelta
import torch

def translate_subtitle(text, source_lang, target_lang):
    translator = Translator()
    translation = translator.translate(text, src=source_lang, dest=target_lang)
    return translation.text

def get_subtitle(inputName):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = whisper.load_model("base").to(device) 
    result = model.transcribe(inputName, fp16=False)
    segments = result['segments']

    # Create a directory for SRT files if it doesn't exist
    srt_directory = "srtFiles"
    if not os.path.exists(srt_directory):
        os.makedirs(srt_directory)

    srtFilename = os.path.join(srt_directory, "subtitle.srt")

    with open(srtFilename, 'w', encoding='utf-8') as srtFile:
        for segment_id, segment in enumerate(segments, start=1):
            start_time = str(timedelta(seconds=int(segment['start']))) + ',000'
            end_time = str(timedelta(seconds=int(segment['end']))) + ',000'
            text = segment['text']
            text_translate = translate_subtitle(text, 'zh-cn', 'vi')

            srt_segment = f"{segment_id}\n{start_time} --> {end_time}\n{text}\n\n"
            srt_segment_translate = f"{segment_id}\n{start_time} --> {end_time}\n{text_translate}\n\n"

            srtFile.write(srt_segment)
            srtFile.write(srt_segment_translate)

# Example usage
if __name__ == "__main__":
    input_audio_file = "temp_audio.wav"
    get_subtitle(input_audio_file)
