from PySide6.QtWidgets import QMainWindow, QDockWidget, QPlainTextEdit, QListWidget
from PySide6.QtCore import Qt
from editor import EditorTabs
from fileexplorer import FileExplorerDock

class IDEMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Minimal IDE Prototype")
        self.resize(1200, 800)

        # Create the menu bar
        self._create_menu_bar()

        # Editor in the center
        self.editor_tabs = EditorTabs()
        self.setCentralWidget(self.editor_tabs)

        # File Explorer on the left
        self.file_explorer_dock = FileExplorerDock(self)
        self.file_explorer_dock.file_double_clicked = self.editor_tabs.open_file
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_explorer_dock)

        # Outline on the right (placeholder)
        self.outline_dock = QDockWidget("Outline", self)
        self.outline_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        outline_list = QListWidget()
        outline_list.addItem("Function: main()")
        outline_list.addItem("Class: ExampleClass")
        outline_list.addItem("def helper_function()")
        self.outline_dock.setWidget(outline_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.outline_dock)

        # Terminal at the bottom (placeholder)
        self.terminal_dock = QDockWidget("Terminal", self)
        self.terminal_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        terminal = QPlainTextEdit(">>> ")
        self.terminal_dock.setWidget(terminal)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminal_dock)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        # File Menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Open")   # Placeholder action
        file_menu.addAction("Save")   # Placeholder action
        file_menu.addAction("Exit")   # Placeholder action

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Cut")    # Placeholder action
        edit_menu.addAction("Copy")   # Placeholder action
        edit_menu.addAction("Paste")  # Placeholder action

        # Settings Menu
        settings_menu = menu_bar.addMenu("Settings")
        settings_menu.addAction("Preferences") # Placeholder action
