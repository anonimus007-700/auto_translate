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
    def __init__(self, url: str, _callback=None):
        self.url = url
        self._callback = _callback
        
        self.folder_path = 'assets'
        self.progress = 0
        self.line_width = 7
    
        self.language = 'ua'      # ua en
        self.model_id = 'v4_ua'   # v4_ua v3_en
        self.sample_rate = 48000  # 8000, 24000, 48000
        self.speaker = 'mykyta'   # mykyta en_0
        self.device = torch.device('cpu')

        self.model_silero, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                    model='silero_tts',
                                    language=self.language,
                                    speaker=self.model_id)

        self.model_silero.to(self.device)
        
        self.model = whisper.load_model('base')
        
        self.__callback('Deleting old files')
        
        self.file_check()
        self.download_video()
        self.separate_audio()

        self.recognize_audio()
        self.audize()
        
        self.fragments_orig()
        self.mix_audio()
    
    def __callback(self, description: str, plus: bool=False):
        if self._callback and plus:
            self.progress += 1
            self._callback({
                    'progress': self.progress,
                    'line_width': self.line_width,
                    'next_description': description
                })
        elif self._callback:
            self._callback({
                    'progress': self.progress,
                    'line_width': self.line_width,
                    'next_description': description
                })
    
    def file_check(self):
        description = 'Download video'

        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        files_to_check = ['output_video.mp4', 'video.mp4', 'audio.wav']

        for file in files_to_check:
            file_path = os.path.join(self.folder_path, file)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        self.__callback(description, True)

    def download_video(self):
        description = 'Separating audio'
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(self.folder_path, 'video.%(ext)s')  # Save file as <title>.<ext>
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

        self.__callback(description, True)
    
    def separate_audio(self):
        description = 'Word recognition'
        
        self.output_video_path = os.path.join(self.folder_path, 'video.mp4')
        self.video = VideoFileClip(str(self.output_video_path))

        audio = self.video.audio

        self.output_audio_path = os.path.join(self.folder_path, 'audio.wav')
        audio.write_audiofile(self.output_audio_path)
        
        self.__callback(description, True)
    

    def recognize_audio(self):
        description = 'Voicing of fragments'
        
        result = self.model.transcribe(self.output_audio_path, word_timestamps=True)

        self.final = []
        self.line_width += len(result['segments'])
        
        for segment in result['segments']:
            start = segment['start']
            end = segment['end']
            text = segment['text']
            translated = GoogleTranslator(source='auto', target='uk').translate(text)
            self.final.append({'timestamp': (float(f'{start:.2f}'), float(f'{end:.2f}')), 'text': translated})
        
        self.__callback(description, True)
    
    def audize(self):
        description = 'Voicing of fragments'
        
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
            
            self.__callback(description, True)

            return {'start_time': start_time, 'end_time': end_time + 0.5, 'audio': audio}

        self.alt = df.apply(generate_audio, axis=1).tolist()

        self.__callback('Fragments without words', True)

    def fragments_orig(self):
        description = 'Mixing audio and video'
        
        chunks_data = []
        waveform, sample_rate = torchaudio.load(self.output_audio_path)

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

        self.__callback(description, True)

    def mix_audio(self):
        description = 'Complite'
        
        df1 = pd.DataFrame(self.alt)
        df2 = pd.DataFrame(self.chunks)
        
        df = pd.concat([df1, df2], ignore_index=True)
        df = df.sort_values(by=['start_time', 'end_time']).reset_index(drop=True)

        # df['end_time'] = df['start_time'] + df['audio'].apply(lambda x: len(x) / self.sample_rate)
        
        print(df)

        total_duration = df['end_time'].max()
        total_samples = int(total_duration * self.sample_rate)

        combined_audio = torch.zeros(total_samples)

        for _, row in df.iterrows():
            start_sample = int(row['start_time'] * self.sample_rate)
            audio_data = row['audio']
            end_sample = start_sample + len(audio_data)

            if end_sample > total_samples:
                print(f'Warning: audio segment exceeds total duration at {row['start_time']}s.')
                end_sample = total_samples

            combined_audio[start_sample:end_sample] = audio_data[:end_sample - start_sample]

        torchaudio.save(self.output_audio_path, combined_audio.unsqueeze(0), self.sample_rate)

        audio = AudioFileClip(self.output_audio_path)
        
        video_path = os.path.join(self.folder_path, 'output_video.mp4')
        
        video_with_audio = self.video.set_audio(audio)
        video_with_audio.write_videofile(video_path, codec='libx264', audio_codec='aac')

        self.__callback(description, True)
    

if __name__ == '__main__':
    auto = AutoTranslate('https://www.youtube.com/shorts/43Dlqi7SJq4')
    # auto = AutoTranslate('https://www.youtube.com/watch?v=PTAI7NXHX0I')
    # auto = AutoTranslate('https://www.youtube.com/watch?v=owePZqppYWM')
    print('Complite!')


# winget install ffmpeg
