import flet as ft

from validators import url
from auto_translate import AutoTranslate

import os


def main(page: ft.Page):
    def progress_callback(e):
        progress_ring.value = e['progress'] / e['line_width']
        
        if e['progress'] / e['line_width'] == 1:
            page.close(progress_dlg)
        
        progress_label.value = e['next_description']

        page.update()

    def submit(e):
        progress_ring.value = 0
        progress_label.value = 'Starting...'
        url_text = url_field.value

        if url(url_text):
            page.open(progress_dlg)
            auto = AutoTranslate(url_text, _callback=progress_callback)

            if video.visible == False:
                video.visible = True
        else:
            page.open(not_url)
        
        video.next()
        url_field.value = ''
        
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
    
    url_field = ft.TextField(label="YouTube URL", hint_text="Please enter URL here")
    submit_but = ft.ElevatedButton("Submit", on_click=submit)
    
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
        title=ft.Text("URL is incorrect!"),
        actions=[
            ft.TextButton("OK", on_click=lambda e: page.close(not_url)),
        ],
    )
    
    progress_ring = ft.ProgressRing()
    progress_label = ft.Text('Starting...')
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
                        ft.Text("Auto Transtate", font_family="Yokai", size=50),
                        video,
                        url_field,
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