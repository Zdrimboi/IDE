from PySide6.QtWidgets import QDockWidget, QTreeView, QFileSystemModel
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import Qt, QDir


class FileExplorerDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("File Explorer", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Set up a QFileSystemModel to display the file system
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())

        # Only show files and directories
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.Files | QDir.Dirs)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        # Hide some columns (for a cleaner look)
        self.tree_view.setColumnHidden(1, True)  # size
        self.tree_view.setColumnHidden(2, True)  # file type
        self.tree_view.setColumnHidden(3, True)  # date modified
        
        # Expand to current directory
        self.tree_view.setRootIndex(self.model.index(QDir.currentPath()))

        # Double-click signal: when user double clicks a file, we emit the file path
        self.tree_view.doubleClicked.connect(self._on_file_double_clicked)

        self.setWidget(self.tree_view)

        # A signal-like property to connect to outside:
        self.file_double_clicked = None

    def _on_file_double_clicked(self, index):
        # Get the file path
        file_path = self.model.filePath(index)
        # If it's a file (not a directory), we want to open it
        if not self.model.isDir(index):
            if self.file_double_clicked:
                self.file_double_clicked(file_path)
