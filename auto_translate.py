import yt_dlp
from moviepy.editor import VideoFileClip, AudioFileClip

import torch
import pandas as pd
import torchaudio
import sounddevice as sd

import whisper

from deep_translator import GoogleTranslator

import os


class AutoTranslate:
    def __init__(self, url: str):
        self.url = url
    
        self.language = 'ua'    # ua en
        self.model_id = 'v4_ua' # v4_ua v3_en
        self.sample_rate = 48000 # 8000, 24000, 48000
        self.speaker = 'mykyta' # mykyta en_0
        self.device = torch.device('cpu')

        self.model_silero, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                    model='silero_tts',
                                    language=self.language,
                                    speaker=self.model_id)

        self.model_silero.to(self.device)
        
        self.model = whisper.load_model("base")
        
        self.file_check()
        self.download_video()

        self.recognize_audio()
        self.audize()
        
        self.fragments_orig()
        self.mix_audio()
    
    def file_check(self):
        files_to_check = ["output_video.mp4", "output.wav", "video.mp4", "audio.wav"]

        for file in files_to_check:
            if os.path.exists(file):
                os.remove(file)

    def download_video(self):
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.%(ext)s',  # Save file as <title>.<ext>
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])
        
        self.video = VideoFileClip("video.mp4")

        audio = self.video.audio
        audio.write_audiofile("audio.wav")
    

    def recognize_audio(self):
        result = self.model.transcribe("audio.wav", word_timestamps=True)

        self.final = []
        
        for segment in result['segments']:
            start = segment['start'] + 0.1
            end = segment['end'] + 0.1
            text = segment['text']
            translated = GoogleTranslator(source='auto', target='uk').translate(text)
            self.final.append({'timestamp': (float(f"{start:.2f}"), float(f"{end:.2f}")), 'text': translated})
    
    def audize(self):
        chunks_data = [{'start_time': chunk['timestamp'][0], 'end_time': chunk['timestamp'][1], 'text': chunk['text']}\
                for chunk in self.final]
        df = pd.DataFrame(chunks_data)

        self.prev_end_time = None

        self.alt = [None] * len(df)

        def generate_audio(row):
            audio = self.model_silero.apply_tts(
                text=row['text'],
                speaker=self.speaker,
                sample_rate=self.sample_rate
            )

            num_samples = audio.shape[0]
            duration_seconds = num_samples / self.sample_rate

            start_time = row['start_time']
            end_time = row['end_time']

            if self.prev_end_time is not None and self.prev_end_time > start_time:
                start_time = self.prev_end_time

            if (end_time - start_time) < duration_seconds:
                difference = duration_seconds - (end_time - start_time)
                end_time = end_time + difference

            self.prev_end_time = end_time

            return {'start_time': start_time, 'end_time': end_time, 'audio': audio}

        self.alt = df.apply(generate_audio, axis=1).tolist()

    def fragments_orig(self):
        chunks_data = []
        waveform, sample_rate = torchaudio.load("audio.wav")

        for i, chunk in enumerate(self.alt):
            start_time = chunk['end_time']

            if i == 0 and chunk['start_time'] > 0:
                chunks_data.append({'start_time': 0, 'end_time': self.alt[i]['start_time']})
            
            if i + 1 < len(self.alt):
                end_time = self.alt[i + 1]['start_time'] 
            else:
                num_samples = waveform.size(1)
                end_time = num_samples / sample_rate
            
            chunks_data.append({'start_time': start_time, 'end_time': end_time})

        df = pd.DataFrame(chunks_data)
        
        self.chunks = [None] * len(df)
        
        def get_samples(row):
            start_sample = int(row['start_time'] * sample_rate)
            end_sample = int(row['end_time'] * sample_rate)

            chunk_waveform = waveform[:, start_sample:end_sample].flatten()
            
            return {'start_time': row['start_time'], 'end_time': row['end_time'], 'audio': chunk_waveform}
            
        self.chunks = df.apply(get_samples, axis=1).tolist()

    def mix_audio(self):
        sample_rate = 48000
        
        df1 = pd.DataFrame(self.alt)
        df2 = pd.DataFrame(self.chunks)
        
        df = pd.concat([df1, df2], ignore_index=True)
        df = df.sort_values(by=['start_time', 'end_time']).reset_index(drop=True)
        
        print(df)
        
        # df = df1

        df['end_time'] = df['start_time'] + df['audio'].apply(lambda x: len(x) / sample_rate)

        total_duration = df['end_time'].max()
        total_samples = int(total_duration * sample_rate)

        combined_audio = torch.zeros(total_samples)

        for _, row in df.iterrows():
            start_sample = int(row['start_time'] * sample_rate)
            audio_data = row['audio']
            end_sample = start_sample + len(audio_data)

            if end_sample > total_samples:
                print(f"Warning: audio segment exceeds total duration at {row['start_time']}s.")
                end_sample = total_samples

            combined_audio[start_sample:end_sample] = audio_data[:end_sample - start_sample]

        torchaudio.save("output.wav", combined_audio.unsqueeze(0), sample_rate)

        audio = AudioFileClip("output.wav")
        
        video_with_audio = self.video.set_audio(audio)
        video_with_audio.write_videofile("output_video.mp4", codec="libx264", audio_codec="aac")
    

if __name__ == "__main__":
    # auto = AutoTranslate('https://www.youtube.com/shorts/Gno-zBED01Y')
    auto = AutoTranslate('https://www.youtube.com/watch?v=PTAI7NXHX0I')
    # auto = AutoTranslate('https://www.youtube.com/watch?v=owePZqppYWM')
    print('Complite!')


# winget install ffmpeg
