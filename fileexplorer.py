import os
from PySide6.QtWidgets import QDockWidget, QTreeView, QMenu, QInputDialog, QMessageBox, QAbstractItemView, QFileSystemModel
from PySide6.QtCore import Qt, QDir, QModelIndex
from PySide6.QtGui import QAction

class FileExplorerDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("File Explorer", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        # Allow renaming
        self.model.setReadOnly(False)

        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.Files | QDir.Dirs)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setColumnHidden(1, True)  # size
        self.tree_view.setColumnHidden(2, True)  # file type
        self.tree_view.setColumnHidden(3, True)  # last modified date
        self.tree_view.setRootIndex(self.model.index(QDir.currentPath()))

        # Allow editing items (for rename)
        self.tree_view.setEditTriggers(QAbstractItemView.SelectedClicked | 
                                       QAbstractItemView.EditKeyPressed | 
                                       QAbstractItemView.DoubleClicked)

        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.doubleClicked.connect(self._on_file_double_clicked)
        self.tree_view.customContextMenuRequested.connect(self._on_context_menu)

        self.setWidget(self.tree_view)

        # Callable property for file double-click integration
        self.file_double_clicked = None

    def _on_file_double_clicked(self, index: QModelIndex):
        file_path = self.model.filePath(index)
        # If it's a file (not a directory), open it
        if not self.model.isDir(index):
            if self.file_double_clicked:
                self.file_double_clicked(file_path)

    def _on_context_menu(self, pos):
        index = self.tree_view.indexAt(pos)
        if not index.isValid():
            return

        file_path = self.model.filePath(index)
        menu = QMenu(self)

        new_file_action = QAction("New File", self)
        new_folder_action = QAction("New Folder", self)
        rename_action = QAction("Rename", self)
        delete_action = QAction("Delete", self)

        # Determine directory in which to create new files/folders
        file_is_dir = self.model.isDir(index)
        if file_is_dir:
            directory_path = file_path
        else:
            parent_index = self.model.parent(index)
            directory_path = self.model.filePath(parent_index)

        new_file_action.triggered.connect(lambda: self._create_new_file(directory_path))
        new_folder_action.triggered.connect(lambda: self._create_new_folder(directory_path))
        rename_action.triggered.connect(lambda: self._rename_item(index))
        delete_action.triggered.connect(lambda: self._delete_item(file_path))

        menu.addAction(new_file_action)
        menu.addAction(new_folder_action)
        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.exec(self.tree_view.mapToGlobal(pos))

    def _create_new_file(self, directory_path):
        file_name, ok = QInputDialog.getText(self, "New File", "Enter new file name:")
        if ok and file_name:
            new_file_path = os.path.join(directory_path, file_name)
            try:
                with open(new_file_path, 'w', encoding='utf-8'):
                    pass
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Unable to create file:\n{e}")
            # QFileSystemModel should update automatically

    def _create_new_folder(self, directory_path):
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter new folder name:")
        if ok and folder_name:
            new_folder_path = os.path.join(directory_path, folder_name)
            try:
                os.mkdir(new_folder_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Unable to create folder:\n{e}")
            # QFileSystemModel should update automatically

    def _rename_item(self, index):
        # Put the item into edit mode so user can rename
        self.tree_view.edit(index)
        # After the user confirms (presses Enter), QFileSystemModel attempts rename.

    def _delete_item(self, file_path):
        reply = QMessageBox.question(
            self, "Confirm Delete", f"Are you sure you want to delete:\n{file_path}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            index = self.model.index(file_path)
            if self.model.isDir(index):
                # Directory deletion: only if empty
                if not os.listdir(file_path):
                    QDir().rmdir(file_path)
                else:
                    QMessageBox.warning(self, "Error", "Directory is not empty.")
            else:
                # File deletion
                try:
                    os.remove(file_path)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Unable to delete file:\n{e}")
            # Changes should appear automatically in the tree view
