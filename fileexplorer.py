import os
import webbrowser
from PySide6.QtWidgets import (QDockWidget, QTreeView, QMenu, QInputDialog, 
                               QMessageBox, QAbstractItemView, QApplication,
                                 QFileSystemModel)
from PySide6.QtCore import Qt, QDir, QModelIndex, QUrl
from PySide6.QtGui import QAction, QDesktopServices

class FileExplorerDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("File Explorer", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.model = QFileSystemModel()
        self.model.setReadOnly(False)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setColumnHidden(1, True)  # size
        self.tree_view.setColumnHidden(2, True)  # file type
        self.tree_view.setColumnHidden(3, True)  # last modified date
        self.tree_view.setEditTriggers(
            QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed | QAbstractItemView.DoubleClicked
        )
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.doubleClicked.connect(self._on_file_double_clicked)
        self.tree_view.customContextMenuRequested.connect(self._on_context_menu)
        self.set_root_directory(QDir.currentPath())  # Default root
        self.setWidget(self.tree_view)

        self.file_double_clicked = None

    def set_root_directory(self, path):
        """Set the root directory of the file explorer."""
        self.model.setRootPath(path)
        self.tree_view.setRootIndex(self.model.index(path))

    def _on_file_double_clicked(self, index: QModelIndex):
        file_path = self.model.filePath(index)
        if not self.model.isDir(index):
            if self.file_double_clicked:
                self.file_double_clicked(file_path)

    def _on_context_menu(self, pos):
        index = self.tree_view.indexAt(pos)
        menu = QMenu(self)

        # Determine directory in which to create new files/folders
        if index.isValid():
            file_path = self.model.filePath(index)
            file_is_dir = self.model.isDir(index)
            if file_is_dir:
                directory_path = file_path
            else:
                parent_index = self.model.parent(index)
                directory_path = self.model.filePath(parent_index)
        else:
            # Clicked on empty space, use the root directory
            directory_path = self.model.rootPath()
            file_is_dir = True
            file_path = None

        # Actions available always (new file, new folder)
        new_file_action = QAction("New File", self)
        new_folder_action = QAction("New Folder", self)
        new_file_action.triggered.connect(lambda: self._create_new_file(directory_path))
        new_folder_action.triggered.connect(lambda: self._create_new_folder(directory_path))
        menu.addAction(new_file_action)
        menu.addAction(new_folder_action)

        if index.isValid():
            # Actions for valid file/folder
            open_location_action = QAction("Open file location", self)
            copy_abs_path_action = QAction("Copy absolute path", self)
            copy_rel_path_action = QAction("Copy relative path", self)
            rename_action = QAction("Rename", self)
            delete_action = QAction("Delete", self)

            open_location_action.triggered.connect(lambda: self._open_file_location(file_path, file_is_dir))
            copy_abs_path_action.triggered.connect(lambda: self._copy_to_clipboard(file_path))
            copy_rel_path_action.triggered.connect(lambda: self._copy_relative_path(file_path))
            rename_action.triggered.connect(lambda: self._rename_item(index))
            delete_action.triggered.connect(lambda: self._delete_item(file_path))

            menu.addAction(open_location_action)
            menu.addAction(copy_abs_path_action)
            menu.addAction(copy_rel_path_action)
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

    def _create_new_folder(self, directory_path):
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter new folder name:")
        if ok and folder_name:
            new_folder_path = os.path.join(directory_path, folder_name)
            try:
                os.mkdir(new_folder_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Unable to create folder:\n{e}")

    def _rename_item(self, index):
        self.tree_view.edit(index)

    def _delete_item(self, file_path):
        reply = QMessageBox.question(
            self, "Confirm Delete", f"Are you sure you want to delete:\n{file_path}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if os.path.isdir(file_path):
                if not os.listdir(file_path):
                    QDir().rmdir(file_path)
                else:
                    QMessageBox.warning(self, "Error", "Directory is not empty.")
            else:
                try:
                    os.remove(file_path)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Unable to delete file:\n{e}")

    def _open_file_location(self, file_path, is_dir):
        # If is_dir is True, file_path is a directory. If not, get its parent directory.
        directory = file_path if is_dir else os.path.dirname(file_path)
        if os.path.isdir(directory):
            # Open directory in the system file explorer
            QDesktopServices.openUrl(QUrl.fromLocalFile(directory))

    def _copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def _copy_relative_path(self, file_path):
        root_path = self.model.rootPath()
        relative = os.path.relpath(file_path, root_path)
        self._copy_to_clipboard(relative)

    def show_file_in_explorer(self, file_path):
        if file_path and os.path.exists(file_path):
            index = self.model.index(file_path)
            if index.isValid():
                self.tree_view.setCurrentIndex(index)
                self.tree_view.scrollTo(index, QAbstractItemView.PositionAtCenter)
