from qtpy.QtWidgets import QComboBox
from harvesters_gui.utils import get_system_font
from harvesters_gui.widgets.canvas import Canvas2D


class ComboBoxDisplayRateList(QComboBox):
    _dict_disp_rates = {"30 fps": 0, "60 fps": 1}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(get_system_font())
        for d in self._dict_disp_rates:
            self.addItem(d)
        self.setCurrentIndex(self._dict_disp_rates["30 fps"])
        self.currentTextChanged.connect(self._set_display_rate)

    def _set_display_rate(self, value):
        if value == "30 fps":
            display_rate = 30.0
        else:
            display_rate = 60.0

        canvas: Canvas2D = self.parent().parent().canvas  # type: ignore
        canvas.display_rate = display_rate
