import flet as ft


def get_tooltip_icon(text: str) -> ft.Icon:
    return ft.Icon(ft.Icons.INFO, color=ft.Colors.PINK, tooltip=text)


class TooltipTexts:

    @property
    def hydrofia_file(self):
        return '\n'.join([
            'Här väljer du vilken txt-fil från HydroFIA som du vill skapa en rättningsmall i excel av.\n '
            'Excelfilen skapar du för att enkelt kunna granska och rätta din HydroFIA rapport.\n '
            'Välj vilken mapp du vill att filen ska sparas i. filtrera på rätt månad och år vid behov'
        ])

    @property
    def template_file(self):
        return '\n'.join([
            'Här sammanfogar du HydroFIA- med CTD-data för att beräkna pH vid Insitu S och T. Fyll i din signatur,\n '
            'namnge projekt (BAS). Ändra vid behov tjocklek på ytlagret, bottenlagret och maximal diff mellan djup,\n '
            'detta för att rätt värde ska hämtas från CTD profil'
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

