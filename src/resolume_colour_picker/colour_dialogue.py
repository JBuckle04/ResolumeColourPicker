from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QStyledItemDelegate, QColorDialog, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor


class ColourTableModel(QAbstractTableModel):
    """Model for storing colour labels and hex values."""
    
    def __init__(self, colours: dict, parent=None):
        super().__init__(parent)
        # Store as ordered list of (label, hex)
        self._data = list(colours.items())

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 2  # Label, Hex

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row, col = index.row(), index.column()
        label, hex_val = self._data[row]
        if role in (Qt.DisplayRole, Qt.EditRole):
            return label if col == 0 else hex_val
        if role == Qt.BackgroundRole and col == 1:
            return QColor(hex_val)
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False
        row, col = index.row(), index.column()
        label, hex_val = self._data[row]
        if col == 0:
            self._data[row] = (value.strip(), hex_val)
        elif col == 1:
            self._data[row] = (label, value.strip())
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def insertRow(self, row, parent=QModelIndex(), label="new colour", hex_val="#ffffff"):
        self.beginInsertRows(parent, row, row)
        self._data.insert(row, (label, hex_val))
        self.endInsertRows()
        return True

    def removeRow(self, row, parent=QModelIndex()):
        if 0 <= row < len(self._data):
            self.beginRemoveRows(parent, row, row)
            self._data.pop(row)
            self.endRemoveRows()
            return True
        return False

    def get_all_colours(self):
        return dict(self._data)


class ColourDelegate(QStyledItemDelegate):
    """Delegate to handle colour picking for hex column."""
    
    def createEditor(self, parent, option, index):
        if index.column() == 1:
            # Non-native QColorDialog approach
            colour = QColor(index.model().data(index, Qt.DisplayRole))
            dlg = QColorDialog(colour, parent)
            dlg.setOption(QColorDialog.DontUseNativeDialog, True)
            if dlg.exec():
                new_colour = dlg.currentColor().name()
                index.model().setData(index, new_colour)
            return None  # no persistent editor
        else:
            return QLineEdit(parent)


class ColourConfigDialog(QDialog):
    """Dialog for configuring colour palette safely using QTableView."""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Configure Colour Palette")
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        info_label = QLabel("Edit colour labels and pick hex values. Must have exactly 8 colours.")
        layout.addWidget(info_label)
        
        # Table
        self.model = ColourTableModel(self.config.get("COLOUR_SET", {}))
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setItemDelegate(ColourDelegate())
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        new_btn = QPushButton("New")
        delete_btn = QPushButton("Delete")
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        new_btn.clicked.connect(self.add_row)
        delete_btn.clicked.connect(self.delete_row)
        save_btn.clicked.connect(self.save_changes)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(new_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def add_row(self):
        row = self.model.rowCount()
        index = 0
        # generate unique label
        while any(f"new colour ({index})" == label for label, _ in self.model._data):
            index += 1
        self.model.insertRow(row, label=f"new colour ({index})")

    def delete_row(self):
        selected = self.table.selectionModel().selectedRows()
        for index in sorted([r.row() for r in selected], reverse=True):
            self.model.removeRow(index)

    def save_changes(self):
        self.config["COLOUR_SET"] = self.model.get_all_colours()
        self.accept()
