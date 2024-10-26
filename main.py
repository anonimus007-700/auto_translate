import flet as ft

from validators import url
from auto_translate import AutoTranslate

import os

# font_yokai_path = os.path.join("assets", "Yokai.otf")

def main(page: ft.Page):
    def progress_callback(e):
        progress_ring.value = e['progress'] / e['line_width']
        
        if e['progress'] / e['line_width'] == 1:
            page.close(progress_dlg)

        page.update()

    def submit(e):
        url_text = url_field.value

        if url(url_text):
            page.open(progress_dlg)
            auto = AutoTranslate(url_text, _callback=progress_callback)
        else:
            page.open(not_url)
            
        
    page.theme_mode = ft.ThemeMode.DARK
    page.title = "Auto Transtate"
    page.window.always_on_top = True
    page.spacing = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme = ft.Theme(color_scheme_seed='indigo')

    page.fonts = {
        "Yokai": "Yokai.otf"
    }
    
    url_field = ft.TextField(label="YouTube URL", hint_text="Please enter URL here")
    submit_but = ft.ElevatedButton("Submit", on_click=submit)

    not_url = ft.CupertinoAlertDialog(
        title=ft.Text("URL is incorrect!"),
        actions=[
            ft.TextButton("OK", on_click=lambda e: page.close(not_url)),
        ],
    )
    
    progress_ring = ft.ProgressRing(semantics_label = 'zxc')
    progress_dlg = ft.CupertinoAlertDialog(
        modal=True,
        content=ft.Container(
            content=progress_ring,
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