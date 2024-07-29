from qtpy.QtGui import QIcon
from harvesters_gui.utils import get_package_root


class Icon(QIcon):
    def __init__(self, file_name):
        super().__init__(get_package_root() + "/images/icon/" + file_name)
