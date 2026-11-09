"""Layout constants for the GUI. Change sizes and spacing here."""

import flet as ft

# Page. The window starts maximized. Below this height the content keeps its
# size and the page scrolls instead, so no card is cut. The left column with the
# CRM tab is the tallest content and needs about 970.
PAGE_PADDING = 10
MIN_PAGE_HEIGHT = 980

# Share of the left column height for the pH and CTD cards. The ratio matches
# their content (about 444 and 316 high), so at MIN_PAGE_HEIGHT both fit
# exactly and with more room both grow.
PH_CARD_EXPAND = 7
DEPTH_CARD_EXPAND = 5

# Cards
CARD_PADDING = 10
CARD_RADIUS = 10
SIDE_COLUMN_WIDTH = 240
TAB_CONTENT_TOP_PADDING = 10

# Buttons
PATH_BUTTON_WIDTH = 320

# Spacing
TOP_ROW_SPACING = 10
FIELD_COLUMN_SPACING = 20
LABELED_ROW_SPACING = 10
LABELED_ROW_TOP_PADDING = 10

# Text
CARD_TITLE_SIZE = 20
CARD_TITLE_BOTTOM_PADDING = 8
TITLE_SIZE = 16
PATH_TEXT_SIZE = 13
OUTPUT_LABEL_SPACING = 4
HIGHLIGHT_SIZE = 16

# Info dialogs. Position in the window, near the card each dialog belongs to.
INFO_DIALOG_WIDTH = 480
INFO_DIALOG_PADDING = 24
INFO_DIALOG_UPPER_CARD = ft.Alignment(0, -1)
INFO_DIALOG_LOWER_CARD = ft.Alignment(0, 0.2)
INFO_DIALOG_CTD_CARD = ft.Alignment.BOTTOM_LEFT

# Input fields
FIELD_WIDTH = 200
FIELD_DENSE = False
