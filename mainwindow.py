from PySide6.QtWidgets import QMainWindow, QDockWidget, QPlainTextEdit, QListWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QAction
from editor import EditorTabs
from fileexplorer import FileExplorerDock

class IDEMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Minimal IDE Prototype")
        self.resize(1200, 800)

        # Editor in the center
        self.editor_tabs = EditorTabs()
        self.setCentralWidget(self.editor_tabs)
        self.editor_tabs.currentChanged.connect(self._on_tab_changed)

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

        # Create the menu bar
        self._create_menu_bar()

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("File")

        # Instead of adding a separate shortcut, rely on QKeySequence for actions:
        open_action = QAction("Open", self)  # Placeholder for open dialog if needed
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._on_save_file)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")

        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self._on_cut)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self._on_copy)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self._on_paste)

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self._on_undo)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self._on_redo)

        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        # Settings Menu (placeholder)
        settings_menu = menu_bar.addMenu("Settings")
        settings_menu.addAction("Preferences") # Placeholder action

    def _on_save_file(self):
        self.editor_tabs.save_current_file()

    def _on_cut(self):
        editor = self.editor_tabs.current_editor()
        if editor:
            editor.cut()

    def _on_copy(self):
        editor = self.editor_tabs.current_editor()
        if editor:
            editor.copy()

    def _on_paste(self):
        editor = self.editor_tabs.current_editor()
        if editor:
            editor.paste()

    def _on_undo(self):
        editor = self.editor_tabs.current_editor()
        if editor:
            editor.undo()

    def _on_redo(self):
        editor = self.editor_tabs.current_editor()
        if editor:
            editor.redo()

    def _on_tab_changed(self, index):
        # When the user switches tabs, highlight that file in the file explorer
        file_path = self.editor_tabs.current_file_path()
        if file_path:
            self.file_explorer_dock.show_file_in_explorer(file_path)
