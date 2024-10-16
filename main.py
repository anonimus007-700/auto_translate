import pyaudiowpatch as pyaudio
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import threading
import torch
import numpy as np
import orjson
import multiprocessing

model = Model(lang="en-us")

DURATION = 5.0
CHUNK_SIZE = 512

language = 'en'    # ua
model_id = 'v3_en' # v4_ua mykyta_v2
sample_rate = 48000
speaker = 'en_0' # mykyta
device = torch.device('cpu')

model_silero, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                 model='silero_tts',
                                 language=language,
                                 speaker=model_id)
model_silero.to(device)

def grab_audio(queue, stream):
    rec = KaldiRecognizer(model, 100000)

    while True:
        data = stream.read(CHUNK_SIZE)
        
        if rec.AcceptWaveform(data):
            result = orjson.loads(rec.Result())
            if result.get('text'):
                queue.put(result)
                print(result)
        else:
            partial_result = orjson.loads(rec.PartialResult())
            if partial_result.get('partial'):
                queue.put(partial_result, block=False)
                # print(partial_result)

def say(queue):
    while True:
        data = queue.get()
        print(data)

        if 'partial' in data and data['partial']:
            audio = model_silero.apply_tts(text=data['partial'],
                            speaker=speaker,
                            sample_rate=sample_rate)
            sd.play(audio, sample_rate)
            sd.wait()

def main():
    p = pyaudio.PyAudio()
    try:
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
    except OSError:
        print("Looks like WASAPI is not available on the system. Exiting...")
        exit()

    default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
    
    if not default_speakers["isLoopbackDevice"]:
        for loopback in p.get_loopback_device_info_generator():
            """
            Try to find loopback device with same name(and [Loopback suffix]).
            Unfortunately, this is the most adequate way at the moment.
            """
            if default_speakers["name"] in loopback["name"]:
                default_speakers = loopback
                break
        else:
            print("Default loopback output device not found.\n\nRun `python -m pyaudiowpatch` to check available devices.\nExiting...\n")
            exit()
        
    print(f"Recording from: ({default_speakers['index']}){default_speakers['name']}")
    
    stream = p.open(format=pyaudio.paInt16,
            channels=default_speakers["maxInputChannels"],
            rate=int(default_speakers["defaultSampleRate"]),
            frames_per_buffer=CHUNK_SIZE,
            input=True,
            input_device_index=default_speakers["index"]
        )
    print(int(default_speakers["defaultSampleRate"])) # 48000
    
    stream.start_stream()
    
    qu = multiprocessing.Queue()
    
    # Create threads instead of processes
    grab_audio_thread = threading.Thread(target=grab_audio, args=(qu, stream), daemon=True)
    say_thread = threading.Thread(target=say, args=(qu,), daemon=True)

    grab_audio_thread.start()
    say_thread.start()
    
    # Keep the main thread alive
    grab_audio_thread.join()
    say_thread.join()

if __name__ == "__main__":
    main()





# if not os.path.isfile(local_file):
#     torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ua/v4_ua.pt',

# import os
# import torch
# import sounddevice as sd

# language = 'ua'
# model_id = 'v4_ua'
# sample_rate = 48000
# speaker = 'mykyta'
# device = torch.device('cpu')

# model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
#                                      model='silero_tts',
#                                      language=language,
#                                      speaker=model_id)
# model.to(device)  # gpu or cpu

# audio = model.apply_tts(text=example_text,
#                         speaker=speaker,
#                         sample_rate=sample_rate)
# sd.play(audio, sample_rate)
# sd.wait()
