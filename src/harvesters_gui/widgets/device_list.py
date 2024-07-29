from qtpy.QtWidgets import QComboBox
from harvesters._private.core.observer import Observer
from harvesters_gui.utils import get_system_font


class ComboBoxDeviceList(QComboBox, Observer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(get_system_font())

    def update(self):
        if self.parent().parent().harvester_core.has_revised_device_info_list:
            self.clear()
            separator = "::"
            for d in self.parent().parent().harvester_core.device_info_list:
                name = d.vendor
                name += separator
                name += d.model

                try:
                    _ = d.serial_number
                except:  # We know it's too broad:
                    pass
                else:
                    if d.serial_number != "":
                        name += separator
                        name += d.serial_number

                try:
                    _ = d.user_defined_name
                except:  # We know it's too broad:
                    pass
                else:
                    if d.user_defined_name != "":
                        name += separator
                        name += d.user_defined_name

                self.addItem(name)
        self.parent().parent().harvester_core.has_revised_device_info_list = False

        enable = False
        if self.parent().parent().files:
            if self.parent().parent().ia is None:
                enable = True
        self.setEnabled(enable)
