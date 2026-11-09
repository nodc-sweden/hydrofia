import flet as ft

from hydrofia.gui import style
from hydrofia.gui.texts import Texts


def get_info_button(
    heading: str, text: str, dialog_alignment: ft.Alignment
) -> ft.IconButton:
    """Info icon that opens a dialog with the text when clicked.

    Any click closes the dialog, also inside it.
    """
    dialog = ft.AlertDialog(
        content_padding=0,
        # The empty action row otherwise adds a strip that does not react to clicks.
        actions_padding=0,
        alignment=dialog_alignment,
        content=ft.Container(
            content=ft.Column(
                [ft.Text(heading, size=style.CARD_TITLE_SIZE), ft.Text(text)],
                tight=True,
            ),
            width=style.INFO_DIALOG_WIDTH,
            padding=style.INFO_DIALOG_PADDING,
            on_click=lambda e: e.control.page.pop_dialog(),
        ),
    )
    return ft.IconButton(
        icon=ft.Icons.INFO,
        icon_color=ft.Colors.PINK,
        tooltip=Texts.show_help,
        on_click=lambda e: e.control.page.show_dialog(dialog),
    )


class TooltipTexts:
    hydrofia_file = (
        "Här väljer du vilken txt-fil från HydroFIA som du vill skapa en rättningsmall "
        "i Excel av. Excelfilen skapar du för att enkelt kunna granska och rätta din "
        "HydroFIA-rapport. Välj vilken mapp du vill att filen ska sparas i. Filtrera på "
        "rätt månad och år vid behov."
    )
    template_file = (
        "Slår ihop HydroFIA-data med CTD-data och beräknar pH vid in situ-salthalt "
        "och -temperatur. Välj rättningsfilen och mappen med CTD-filer. "
        "Hur proverna matchas ställer du in under CTD-matchning."
    )
    metadata = (
        "Dessa fält behövs för beräkning samt för att fylla i metadata i resultatifilen"
    )
    create_result = "Ange det namn du vill att exportfilen ska ha"
    ctd = (
        "Varje prov får salthalt och temperatur från närmaste djup i CTD-profilen. "
        "Ligger det djupet längre bort än Max avstånd får provet inga CTD-värden. "
        "Gränsen gäller inte för prov inom de angivna avstånden från ytan och botten."
    )
