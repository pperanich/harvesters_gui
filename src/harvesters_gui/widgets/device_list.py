from harvesters.core import Harvester, ImageAcquirer
from qtpy.QtWidgets import QComboBox
from harvesters._private.core.observer import Observer
from harvesters_gui.utils import get_system_font


class ComboBoxDeviceList(QComboBox, Observer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(get_system_font())

    def update(self):  # type: ignore
        harvester_core: Harvester = self.parent().parent().harvester_core  # type: ignore
        ia: ImageAcquirer = self.parent().parent().ia  # type: ignore

        if harvester_core.has_revised_device_info_list:
            self.clear()
            separator = "::"
            for d in harvester_core.device_info_list:
                name = str(d.vendor)
                name += separator
                name += str(d.model)

                try:
                    _ = d.serial_number
                except Exception:  # We know it's too broad:
                    pass
                else:
                    if d.serial_number != "":
                        name += separator
                        name += str(d.serial_number)

                try:
                    _ = d.user_defined_name
                except Exception:  # We know it's too broad:
                    pass
                else:
                    if d.user_defined_name != "":
                        name += separator
                        name += str(d.user_defined_name)

                self.addItem(name)
        harvester_core.has_revised_device_info_list = False

        enable = False
        if harvester_core.files:
            if ia is None:
                enable = True
        self.setEnabled(enable)
