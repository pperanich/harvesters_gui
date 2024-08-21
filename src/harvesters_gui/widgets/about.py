import sys
from qtpy.QtCore import Qt
from qtpy.QtGui import QPainter, QPixmap
from qtpy.QtWidgets import (
    QDialog,
    QApplication,
    QPlainTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QFrame,
    QPushButton,
    QTextEdit,
)

from harvesters import __version__
from harvesters_gui.utils import get_package_root, get_system_font


class DecoratedDialog(QDialog):
    def __init__(self, parent=None, path_to_image=None):
        super().__init__(parent)
        self._path_to_image = path_to_image

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.drawPixmap(
            self.rect(),
            QPixmap(
                get_package_root() + "/_private/frontend/image/background/about.jpg"
            ),
        )


class TransparentLineEdit(QLineEdit):
    def __init__(self, text):
        super().__init__(text)

        self.setReadOnly(True)
        self.setFont(get_system_font())
        self.setStyleSheet("background: rgba(0, 0, 0, 0%)")
        self.setFrame(False)


class TransparentTextEdit(QTextEdit):
    def __init__(self, text):
        super().__init__(text)

        self.setReadOnly(True)
        self.setFont(get_system_font())
        self.setStyleSheet("background: rgba(0, 0, 0, 0%)")
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class About(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About Harvester")

        layout_main = QVBoxLayout()
        layout_textual_info = QVBoxLayout()
        layout_image = QHBoxLayout()

        self._button_acknowledgements = QPushButton()
        self._button_acknowledgements.setText("Acknowledgements")
        self._button_acknowledgements.setFont(get_system_font())
        self._button_acknowledgements.clicked.connect(self._handle_open_dialog)

        text_version = TransparentLineEdit("Version: " + __version__)
        text_copyright = TransparentLineEdit("Copyright (c) 2018 EMVA")

        layout_textual_info.addWidget(text_version)
        layout_textual_info.addWidget(text_copyright)

        image = DecoratedDialog()
        image.setFixedWidth(640)
        image.setFixedHeight(480)

        layout_image.addWidget(image)

        layout_main.addLayout(layout_image)
        layout_main.addLayout(layout_textual_info)
        layout_main.addWidget(self._button_acknowledgements)

        self.setLayout(layout_main)

        self._acknowledgements = Acknowledgements(self)
        self._acknowledgements.setModal(True)

    def _get_version_info(self):
        return "Version " + getattr(self.parent(), "version", "ERROR")

    def _handle_open_dialog(self):
        self._acknowledgements.show()


class Acknowledgements(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Acknowledgements")

        layout = QVBoxLayout(self)

        content = "Cover Drawing:\n"
        content += "\n"
        content += "Pieter Bruegel the Elder, The Harvesters\n"
        content += "Copyright (c) 2000–2018 The Metropolitan Museum of Arts"
        content += "\n\n"
        content += "Open Source Libraries/Resources:\n"
        content += "\n"
        content += "VisPy (BSD)\n"
        content += "Copyright (c) 2013-2018 VisPy developers\n"
        content += "http://vispy.org/"
        content += "\n\n"
        content += "PyQt5 (GPL)\n"
        content += "Copyright (c) 2018 Riverbank Computing Limited\n"
        content += "https://www.riverbankcomputing.com/"
        content += "\n\n"
        content += "Icons8 (Creative Commons Attribution-NoDerivs 3.0 Unported)\n"
        content += "Copyright (c) Icons8 LLC\n"
        content += "https://icons8.comn"
        content += "\n\n"
        content += "Versioneer (Public Domain, CC0-1.0)\n"
        content += "Copyright (c) 2018 Brian Warner\n"
        content += "https://github.com/warner/python-versioneer"

        self._text = QPlainTextEdit(content)
        self._text.setReadOnly(True)
        self._text.setFont(get_system_font())
        self._text.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self._text.setFixedWidth(480)

        layout.addWidget(self._text)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    about = About()
    about.show()
    sys.exit(app.exec())
