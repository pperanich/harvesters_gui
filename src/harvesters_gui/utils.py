import os
from qtpy.QtGui import QFont

from harvesters._private.core.helper.system import (
    is_running_on_macos,
    is_running_on_windows,
)


def get_package_root():
    return os.path.dirname(os.path.abspath(__file__))


def get_system_font():
    if is_running_on_windows():
        font, size = "Calibri", 12
    else:
        if is_running_on_macos():
            font, size = "Lucida Sans Unicode", 14
        else:
            font, size = "Sans-serif", 11
    return QFont(font, size)


def compose_tooltip(description, shortcut_key=None):
    tooltip = description
    if shortcut_key is not None:
        tooltip += " (" + shortcut_key + ")"
    return tooltip
