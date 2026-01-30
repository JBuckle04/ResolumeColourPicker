from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableView, QStyledItemDelegate,
    QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex


class LayerMapModel(QAbstractTableModel):
    """Model for Layer Map: stores (name, value) pairs."""
    
    def __init__(self, layer_map: dict, parent=None):
        super().__init__(parent)
        self._data = [(k, str(v)) for k,v in layer_map.items()]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 2  # Name, Value

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row, col = index.row(), index.column()
        name, value = self._data[row]
        if role in (Qt.DisplayRole, Qt.EditRole):
            return name if col == 0 else str(value)
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False
        row, col = index.row(), index.column()
        name, val = self._data[row]
        value = value.strip() if isinstance(value, str) else str(value)
        if col == 0:
            self._data[row] = (value, val)
        else:
            self._data[row] = (name, value)
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def insertRow(self, row, parent=QModelIndex(), name="new layer", value="0"):
        self.beginInsertRows(parent, row, row)
        self._data.insert(row, (name, value))
        self.endInsertRows()
        return True

    def removeRow(self, row, parent=QModelIndex()):
        if 0 <= row < len(self._data):
            self.beginRemoveRows(parent, row, row)
            self._data.pop(row)
            self.endRemoveRows()
            return True
        return False

    def get_all_layers(self):
        """Return current layer map as dict, preserving order."""
        return dict(self._data)


class LayerDelegate(QStyledItemDelegate):
    """Delegate to handle editable line edits for both columns."""
    
    def createEditor(self, parent, option, index):
        return QLineEdit(parent)


class LayerMapDialog(QDialog):
    """Layer Map dialog using QTableView and model/delegate."""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Layer Map")
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Edit layers:"))
        
        # Model + View
        self.model = LayerMapModel(self.config.get("LAYER_MAP"))
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setItemDelegate(LayerDelegate())
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
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
        # generate unique layer name
        while any(f"new layer ({index})" == name for name, _ in self.model._data):
            index += 1
        self.model.insertRow(row, name=f"new layer ({index})")

    def delete_row(self):
        selected = self.table.selectionModel().selectedRows()
        for index in sorted([r.row() for r in selected], reverse=True):
            self.model.removeRow(index)

    def save_changes(self):
        """Validate and save layer map."""
        new_layer_map = {}
        for name, value in self.model._data:
            name_clean = name.strip()
            val_clean = value.strip().upper()
            if val_clean != "ALL":
                try:
                    val_clean = int(val_clean)
                except ValueError:
                    QMessageBox.critical(
                        self,
                        "Error",
                        'Layer map can be a number or "ALL"'
                    )
                    return
            new_layer_map[name_clean] = val_clean
        self.config["LAYER_MAP"] = new_layer_map
        self.accept()
