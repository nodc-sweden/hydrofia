import math
import flet as ft


def get_tooltip_icon(text: str) -> ft.Icon:
    return ft.Icon(name=ft.icons.INFO, color=ft.colors.PINK, tooltip=text)


class TooltipTexts:

    @property
    def hydrofia_file(self):
        return '\n'.join([
            'Här väljer du vilken exportfil (.txt) från HydroFIA som du vill skapa en excelfil av. ',
            'Excelfilen skapar du för att enkelt kunna granska och rätta din HydroFIA rapport. ',
            'Välj vilken mapp du vill att filen ska sparas i. filtrera på rätt månad och år vid behov'
        ])

    @property
    def template_file(self):
        return '\n'.join([
            'Här sammanfogar du HydroFIA-excel med CTD för att beräkna pH vid Insitu S och T.',
            'Fyll i din signatur, namnge projekt (HydroFIA-BAS ÅÅ-första serie nr).',
            'Ändra vid behov tjocklek på ytlagret, bottenlagret och maximal diff mellan djup,',
            'detta för att rätt värde ska hämtas från CTD profil',
        ])

    @property
    def metadata(self):
        return 'Dessa fält behövs för beräkning samt för att fylla i metadata i resultatifilen'

    # @property
    # def create_template(self):
    #     return 'Ange det namn du vill att excelfilen ska ha (HydroFIA-BAS ÅÅ-första serienr'

    @property
    def create_result(self):
        return 'Ange det namn du vill att exportfilen ska ha'

    @property
    def ctd(self):
        return 'No info'


def get_tooltip_widget(msg):
    return ft.Tooltip(
        message=msg,
        padding=20,
        border_radius=10,
        text_style=ft.TextStyle(size=14, color=ft.colors.WHITE),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.Alignment(0.8, 1),
            colors=[
                "0xff1f005c",
                "0xff5b0060",
                "0xff870160",
                "0xffac255e",
                "0xffca485c",
                "0xffe16b5c",
                "0xfff39060",
                "0xffffb56b",
            ],
            tile_mode=ft.GradientTileMode.MIRROR,
            rotation=math.pi / 3,
        ),
    )