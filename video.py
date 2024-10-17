# import yt_dlp
# from moviepy.editor import VideoFileClip

# video_url = 'https://www.youtube.com/watch?v=rN01ExHHRhk&t'

# ydl_opts = {
#     'format': 'best',
#     'outtmpl': 'video.%(ext)s',  # Save file as <title>.<ext>
# }

# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     ydl.download([video_url])

# video = VideoFileClip("video.mp4")

# audio = video.audio
# audio.write_audiofile("audio.wav")

from transformers import pipeline

model = pipeline("automatic-speech-recognition", model="openai/whisper-base", language='en')
result = model("audio.wav", return_timestamps=True)
print(result)

# winget install ffmpeg
