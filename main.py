import os

import flet as ft

from validators import url
from deep_translator import GoogleTranslator

from auto_translate import AutoTranslate
from change_language import language_list, translations
import set_config


start_language = set_config.set_up()


def main(page: ft.Page):
    def _callback(e):
        progress_ring.value = e['progress'] / e['line_width']
        
        if e['progress'] / e['line_width'] == 1:
            page.close(progress_dlg)
        
        progress_label.value = GoogleTranslator(source='en',
                                                target=language_list[program_language.value]
                                ).translate(e['next_description'])

        page.update()

    def submit(e):
        progress_ring.value = 0
        progress_label.value = translations[language_list[program_language.value]]['progress_label']
        url_text = url_field.value

        if url(url_text):
            page.open(progress_dlg)
            s_lang = select_language.value
            AutoTranslate(url_text, to_language=language_list[s_lang], _callback=_callback)

            if not video.visible:
                video.visible = True
                
            video.next()
            video.pause()
        else:
            page.open(not_url)

        url_field.value = ''
        
        page.update()
    
    def change_language(e):
        program_language.label = translations[language_list[e.data]]['program_language label']
        program_language.hint_text = translations[language_list[e.data]]['program_language hint_text']
        select_language.label = translations[language_list[e.data]]['select_language label']
        select_language.hint_text = translations[language_list[e.data]]['select_language hint_text']
        url_field.label = translations[language_list[e.data]]['url_field label']
        url_field.hint_text = translations[language_list[e.data]]['url_field hint_text']
        submit_but.text = translations[language_list[e.data]]['submit_but']
        not_url.title=ft.Text(translations[language_list[e.data]]['not_url'])
        
        set_config.update(language_list[e.data])
        
        page.update()


    page.theme_mode = ft.ThemeMode.DARK
    page.title = "Auto Transtate"
    page.window.icon = os.path.abspath(os.path.join('assets', 'favicon.ico'))
    page.spacing = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme = ft.Theme(color_scheme_seed='indigo')

    page.fonts = {
        "Yokai": "Yokai.otf"
    }
    
    program_language = ft.Dropdown(
            label=translations[start_language]['program_language hint_text'],
            hint_text=translations[start_language]['program_language hint_text'],
            options=[
                ft.dropdown.Option("Ukraine"),
                ft.dropdown.Option("English"),
                ft.dropdown.Option("German"),
                ft.dropdown.Option("French"),
            ],
            on_change=change_language,
        )
    program_language.value = next((k for k, v in language_list.items() if v == start_language), None)
    
    select_language = ft.Dropdown(
            label=translations[start_language]['select_language hint_text'],
            hint_text=translations[start_language]['select_language hint_text'],
            options=[
                ft.dropdown.Option("Ukraine"),
                ft.dropdown.Option("English"),
                ft.dropdown.Option("German"),
                ft.dropdown.Option("French"),
            ],
        )
    select_language.value = "Ukraine"
    
    url_field = ft.TextField(label=translations[start_language]['url_field label'],
                hint_text=translations[start_language]['url_field hint_text'])
    submit_but = ft.ElevatedButton(translations[start_language]['submit_but'],
                                   on_click=submit)
    
    output_video = [
                    ft.VideoMedia(
                        "assets/output_video.mp4"
                    ),
                    ft.VideoMedia(
                        "assets/output_video.mp4"
                    ),
                ]
    video = ft.Video(
                expand=True,
                playlist=output_video,
                playlist_mode=ft.PlaylistMode.LOOP,
                aspect_ratio=16/9,
                volume=100,
                autoplay=False,
                filter_quality=ft.FilterQuality.HIGH,
                muted=False,
                visible=True if os.path.exists(os.path.join('assets', 'output_video.mp4')) else False,
            )

    not_url = ft.CupertinoAlertDialog(
        title=ft.Text(translations[start_language]['not_url']),
        actions=[
            ft.TextButton("OK", on_click=lambda e: page.close(not_url)),
        ],
    )

    progress_ring = ft.ProgressRing()
    progress_label = ft.Text()
    progress_dlg = ft.CupertinoAlertDialog(
        modal=True,
        content=ft.Container(
            content=ft.Column(
                        [
                            progress_ring,
                            progress_label,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
            width=150,
            height=150,
            padding=50,
            alignment=ft.alignment.center,
        ),
    )

    page.add(
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Row([
                            ft.Text("Auto Transtate", font_family="Yokai", size=50),
                            program_language
                        ]),
                        video,
                        ft.Row([url_field, select_language]),
                        submit_but
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

ft.app(main, assets_dir="assets")