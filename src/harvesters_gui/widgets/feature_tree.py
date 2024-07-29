import re
import sys
from typing import Optional
from qtpy.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from qtpy.QtWidgets import (
    QApplication,
    QTreeView,
    QSpinBox,
    QPushButton,
    QComboBox,
    QWidget,
    QLineEdit,
    QStyledItemDelegate,
)
from qtpy.QtGui import QColor
from genicam.genapi import NodeMap
from genicam.genapi import EInterfaceType, EAccessMode, EVisibility

from harvesters_gui.utils import get_system_font


class TreeItem(object):
    _readable_nodes = [
        EInterfaceType.intfIBoolean,
        EInterfaceType.intfIEnumeration,
        EInterfaceType.intfIFloat,
        EInterfaceType.intfIInteger,
        EInterfaceType.intfIString,
        EInterfaceType.intfIRegister,
    ]

    _readable_access_modes = [EAccessMode.RW, EAccessMode.RO]

    def __init__(self, data=None, parent_item=None):
        super().__init__()

        self._parent_item = parent_item
        self._own_data = data
        self._child_items = []

    @property
    def parent_item(self):
        return self._parent_item

    @property
    def own_data(self):
        return self._own_data

    @property
    def child_items(self):
        return self._child_items

    def appendChild(self, item):
        self.child_items.append(item)

    def child(self, row):
        return self.child_items[row]

    def childCount(self):
        return len(self.child_items)

    def columnCount(self):
        try:
            ret = len(self.own_data)
        except TypeError:
            ret = 1
        return ret

    def data(self, column):
        if isinstance(self.own_data[column], str):
            try:
                return self.own_data[column]
            except IndexError:
                return None
        else:
            value = ""
            feature = self.own_data[column]
            if column == 0:
                value = feature.node.display_name
            else:
                interface_type = feature.node.principal_interface_type

                if interface_type != EInterfaceType.intfICategory:
                    if interface_type == EInterfaceType.intfICommand:
                        value = "[Click here]"
                    else:
                        if (
                            feature.node.get_access_mode()
                            not in self._readable_access_modes
                        ):
                            value = "[Not accessible]"
                        elif interface_type not in self._readable_nodes:
                            value = "[Not readable]"
                        else:
                            try:
                                value = str(feature.value)
                            except AttributeError:
                                try:
                                    value = feature.to_string()
                                except AttributeError:
                                    pass

            return value

    def tooltip(self, column):
        if isinstance(self.own_data[column], str):
            return None
        else:
            feature = self.own_data[column]
            return feature.node.tooltip

    def background(self, column):
        if isinstance(self.own_data[column], str):
            return None
        else:
            feature = self.own_data[column]
            interface_type = feature.node.principal_interface_type
            if interface_type == EInterfaceType.intfICategory:
                return QColor(56, 147, 189, 1)
            else:
                return None

    def foreground(self, column):
        if isinstance(self.own_data[column], str):
            return None
        else:
            feature = self.own_data[column]
            interface_type = feature.node.principal_interface_type
            if interface_type == EInterfaceType.intfICategory:
                return QColor("white")
            else:
                return None

    def parent(self):
        return self._parent_item

    def row(self):
        if self._parent_item:
            return self._parent_item.child_items.index(self)

        return 0


class FeatureTreeModel(QAbstractItemModel):
    #
    _capable_roles = [
        Qt.ItemDataRole.DisplayRole,
        Qt.ItemDataRole.ToolTipRole,
        Qt.ItemDataRole.BackgroundRole,
        Qt.ItemDataRole.ForegroundRole,
    ]

    #
    _editables = [EAccessMode.RW, EAccessMode.WO]

    def __init__(self, parent=None, node_map: Optional[NodeMap] = None):
        """
        REMARKS: QAbstractItemModel might impact the performance and could
        slow Harvester. As far as we've confirmed, QAbstractItemModel calls
        its index() method for every item already shown. Especially, such
        a call happens every time when (1) its view got/lost focus or (2)
        its view was scrolled. If such slow performance makes people
        irritating we should investigate how can we optimize it.

        """
        #
        super().__init__()

        #
        self._root_item = TreeItem(("Feature Name", "Value"))
        self._node_map = node_map
        if node_map:
            self.populateTreeItems(node_map.Root.features, self._root_item)

    @property
    def root_item(self):
        return self._root_item

    def columnCount(self, parent=None, *args, **kwargs):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.root_item.columnCount()

    def data(self, index: QModelIndex, role=None):
        if not index.isValid():
            return None

        if role not in self._capable_roles:
            return None

        item = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            value = item.data(index.column())
        elif role == Qt.ItemDataRole.ToolTipRole:
            value = item.tooltip(index.column())
        elif role == Qt.ItemDataRole.BackgroundRole:
            value = item.background(index.column())
        else:
            value = item.foreground(index.column())

        return value

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        tree_item = index.internalPointer()
        feature = tree_item.own_data[0]
        access_mode = feature.node.get_access_mode()

        if access_mode in self._editables:
            ret = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        else:
            if index.column() == 1:
                ret = Qt.ItemFlag.NoItemFlags
            else:
                ret = Qt.ItemFlag.ItemIsEnabled
        return ret

    def headerData(self, p_int, Qt_Orientation, role=None):
        # p_int: section
        if (
            Qt_Orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return self.root_item.data(p_int)
        return None

    def index(self, p_int, p_int_1, parent=None, *args, **kwargs):
        # p_int: row
        # p_int_1: column
        if not self.hasIndex(p_int, p_int_1, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(p_int)
        if child_item:
            return self.createIndex(p_int, p_int_1, child_item)
        else:
            return QModelIndex()

    def parent(self, index=None):
        if not index.isValid():
            return index

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=None, *args, **kwargs):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.childCount()

    def populateTreeItems(self, features, parent_item):
        for feature in features:
            interface_type = feature.node.principal_interface_type
            item = TreeItem([feature, feature], parent_item)
            parent_item.appendChild(item)
            if interface_type == EInterfaceType.intfICategory:
                self.populateTreeItems(feature.features, item)

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            # TODO: Check the type of the target and convert the given value.
            self.dataChanged.emit(index, index)

            #
            tree_item = index.internalPointer()
            feature = tree_item.own_data[0]
            interface_type = feature.node.principal_interface_type
            try:
                if interface_type == EInterfaceType.intfICommand:
                    if value:
                        feature.execute()
                elif interface_type == EInterfaceType.intfIBoolean:
                    feature.value = True if value.lower() == "true" else False
                elif interface_type == EInterfaceType.intfIFloat:
                    feature.value = float(value)
                else:
                    feature.value = value
                return True
            except Exception:
                # TODO: Specify appropriate exceptions
                return False


class FeatureEditDelegate(QStyledItemDelegate):
    def __init__(self, proxy, parent=None):
        #
        super().__init__()

        #
        self._proxy = proxy

    def createEditor(
        self, parent: QWidget, QStyleOptionViewItem, proxy_index: QModelIndex
    ):
        # Get the actual source.
        src_index = self._proxy.mapToSource(proxy_index)

        # If it's the column #0, then immediately return.
        if src_index.column() == 0:
            return None

        tree_item = src_index.internalPointer()
        feature = tree_item.own_data[0]
        interface_type = feature.node.principal_interface_type

        if interface_type == EInterfaceType.intfIInteger:
            w = QSpinBox(parent)
            w.setRange(feature.min, feature.max)
            w.setSingleStep(feature.inc)
            w.setValue(feature.value)
        elif interface_type == EInterfaceType.intfICommand:
            w = QPushButton(parent)
            w.setText("Execute")
            w.clicked.connect(lambda: self.on_button_clicked(proxy_index))
        elif interface_type == EInterfaceType.intfIBoolean:
            w = QComboBox(parent)
            boolean_ints = {"False": 0, "True": 1}
            w.addItem("False")
            w.addItem("True")
            proxy_index = (
                boolean_ints["True"] if feature.value else boolean_ints["False"]
            )
            w.setCurrentIndex(proxy_index)
        elif interface_type == EInterfaceType.intfIEnumeration:
            w = QComboBox(parent)
            for item in feature.entries:
                w.addItem(item.symbolic)
            w.setCurrentText(feature.value)
        elif interface_type == EInterfaceType.intfIString:
            w = QLineEdit(parent)
            w.setText(feature.value)
        elif interface_type == EInterfaceType.intfIFloat:
            w = QLineEdit(parent)
            w.setText(str(feature.value))
        else:
            return None

        #
        w.setFont(get_system_font())

        return w

    def setEditorData(self, editor: Optional[QWidget], index: QModelIndex):
        src_index = self._proxy.mapToSource(index)
        value = src_index.data(Qt.ItemDataRole.DisplayRole)
        tree_item = src_index.internalPointer()
        feature = tree_item.own_data[0]
        interface_type = feature.node.principal_interface_type

        if editor is None:
            raise ValueError("Editor must not be None!")

        if interface_type == EInterfaceType.intfIInteger and isinstance(
            editor, QSpinBox
        ):
            editor.setValue(int(value))
        elif interface_type == EInterfaceType.intfIBoolean and isinstance(
            editor, QComboBox
        ):
            i = editor.findText(value, Qt.MatchFlag.MatchFixedString)
            editor.setCurrentIndex(i)
        elif interface_type == EInterfaceType.intfIEnumeration and isinstance(
            editor, QComboBox
        ):
            editor.setEditText(value)
        elif interface_type == EInterfaceType.intfIString and isinstance(
            editor, QLineEdit
        ):
            editor.setText(value)
        elif interface_type == EInterfaceType.intfIFloat and isinstance(
            editor, QLineEdit
        ):
            editor.setText(value)

    def setModelData(
        self,
        editor: Optional[QWidget],
        model: Optional[QAbstractItemModel],
        index: QModelIndex,
    ):
        assert model is not None
        src_index = self._proxy.mapToSource(index)
        tree_item = src_index.internalPointer()
        feature = tree_item.own_data[0]
        interface_type = feature.node.principal_interface_type

        if interface_type == EInterfaceType.intfIInteger and isinstance(
            editor, QSpinBox
        ):
            data = editor.value()
            model.setData(index, data)
        elif interface_type == EInterfaceType.intfIBoolean and isinstance(
            editor, QComboBox
        ):
            data = editor.currentText()
            model.setData(index, data)
        elif interface_type == EInterfaceType.intfIEnumeration and isinstance(
            editor, QComboBox
        ):
            data = editor.currentText()
            model.setData(index, data)
        elif interface_type == EInterfaceType.intfIString and isinstance(
            editor, QLineEdit
        ):
            data = editor.text()
            model.setData(index, data)
        elif interface_type == EInterfaceType.intfIFloat and isinstance(
            editor, QLineEdit
        ):
            data = editor.text()
            model.setData(index, data)

    def on_button_clicked(self, proxy_index: QModelIndex):
        src_index = self._proxy.mapToSource(proxy_index)
        tree_item = src_index.internalPointer()
        feature = tree_item.own_data[0]
        interface_type = feature.node.principal_interface_type

        if interface_type == EInterfaceType.intfICommand:
            feature.execute()


class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self, visibility=EVisibility.Beginner, parent=None):
        #
        super().__init__()

        #
        self._visibility = visibility
        self._keyword = ""

    def filterVisibility(self, visibility):
        beginner_items = {EVisibility.Beginner}
        expert_items = beginner_items.union({EVisibility.Expert})
        guru_items = expert_items.union({EVisibility.Guru})
        all_items = guru_items.union({EVisibility.Invisible})

        items_dict = {
            EVisibility.Beginner: beginner_items,
            EVisibility.Expert: expert_items,
            EVisibility.Guru: guru_items,
            EVisibility.Invisible: all_items,
        }

        if visibility not in items_dict[self._visibility]:
            return False
        else:
            return True

    def filterPattern(self, name):
        if not re.search(self._keyword, name, re.IGNORECASE):
            print(name + ": refused")
            return False
        else:
            print(name + ": accepted")
            return True

    def setVisibility(self, visibility: EVisibility):
        self._visibility = visibility
        self.invalidateFilter()

    def setKeyword(self, keyword: str):
        self._keyword = keyword
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent: QModelIndex):
        src_model = self.sourceModel()
        assert src_model is not None
        src_index = src_model.index(source_row, 0, parent=source_parent)

        tree_item = src_index.internalPointer()
        feature = tree_item.own_data[0]
        name = feature.node.display_name
        visibility = feature.node.visibility
        if len(tree_item.child_items):
            for child in tree_item.child_items:
                if self.filterAcceptsRow(child.row(), src_index):
                    return True
            return False
        else:
            matches = re.search(self._keyword, name, re.IGNORECASE)

        if matches:
            result = self.filterVisibility(visibility)
        else:
            result = False
        return result


if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = FeatureTreeModel()
    view = QTreeView(model)  # type: ignore
    view.show()
    sys.exit(app.exec())
