# Auto Transtale
This program is needed so that you can watch videos in an   unknown language and understand everything

## To do
```bash
pip install -r requirements.txt
```

## This is what the program looks like at first launch
![img](first_start.png)

here we see such fields as "Choose program language" for setting interface languages. 'YouTube URL' for the video to be translated. 'Choose language to translate into' for which language to translate into

## I also made it so that you yourself could install the translation script to your programs

in the file auto_translate.py there is a class AutoTranslate to it you need to pass the following arguments (URL YouTube video) to_language: Literal['uk', 'en', 'fr', 'de'] to which language to translate

```
"Ukraine" = 'uk',
"English" = 'en',
"German" = 'de',
"French" = 'fr'
```

But you can use _callback to know at which stage the program is currently being executed

That will save your output video to the assets/output_video.mp4 folder

## How to use _callback

```python
AutoTranslate(url='https://www.youtube.com/shorts/rIweLp5SjKI', to_language='uk', _callback=_callback)

def _callback(e):
    print('At what stage is the program now', e['progress'])
    print('How many more steps are needed', e['line_width'])
    print('What is currently being done', e['next_description'])
```
