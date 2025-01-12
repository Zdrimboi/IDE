import os
import shlex
from PySide6.QtWidgets import QMainWindow, QDockWidget, QPlainTextEdit, QListWidget, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QAction
from editor import EditorTabs
from fileexplorer import FileExplorerDock
from terminal import TerminalDock
from outline import OutlineDock  # <--- Import your OutlineDock

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

        # Outline on the right
        self.outline_dock = OutlineDock(self)
        self.outline_dock.set_editor_tabs(self.editor_tabs)
        self.addDockWidget(Qt.RightDockWidgetArea, self.outline_dock)

        # Terminal at the bottom
        self.terminal_dock = TerminalDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminal_dock)

        self._create_menu_bar()

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("File")
        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(self._on_open_folder)
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._on_save_file)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(open_folder_action)
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

        # **Run** Menu
        run_action = QAction("Run", self)
        run_action.triggered.connect(self._on_run_file)
        menu_bar.addAction(run_action)

        # View Menu
        view_menu = menu_bar.addMenu("View")
        toggle_file_explorer = QAction("Show File Explorer", self, checkable=True, checked=True)
        toggle_file_explorer.triggered.connect(lambda checked: self._toggle_dock(self.file_explorer_dock, checked))
        
        toggle_outline = QAction("Show Outline", self, checkable=True, checked=True)
        toggle_outline.triggered.connect(lambda checked: self._toggle_dock(self.outline_dock, checked))

        toggle_terminal = QAction("Show Terminal", self, checkable=True, checked=True)
        toggle_terminal.triggered.connect(lambda checked: self._toggle_dock(self.terminal_dock, checked))

        view_menu.addAction(toggle_file_explorer)
        view_menu.addAction(toggle_outline)
        view_menu.addAction(toggle_terminal)

        # # Settings Menu (placeholder)
        # settings_menu = menu_bar.addMenu("Settings")
        # settings_menu.addAction("Preferences") # Placeholder action

    def _on_tab_changed(self, index):
        file_path = self.editor_tabs.current_file_path()
        if file_path:
            self.file_explorer_dock.show_file_in_explorer(file_path)
        self.outline_dock.refresh_outline()

    def _on_save_file(self):
        self.editor_tabs.save_current_file()
        self.outline_dock.refresh_outline()

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

    def _on_open_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Open Folder", "")
        if directory:
            self.file_explorer_dock.set_root_directory(directory)

    def _toggle_dock(self, dock, show):
        if show:
            dock.show()
        else:
            dock.hide()

    def _on_run_file(self):
        file_path = self.editor_tabs.current_file_path()
        if not file_path:
            return  # No file to run

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".py":
            # Use python + shlex.quote for safety
            command = f"python {shlex.quote(file_path)}"
            self.terminal_dock.execute_command(command)

        elif extension == ".c":
            # On Windows, produce "file.exe" output and run it
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            # If using cmd.exe
            command = (
                f"gcc {shlex.quote(file_path)} -o {shlex.quote(base_name)}.exe "
                f"&& .\\{base_name}.exe"
            )
            self.terminal_dock.execute_command(command)
        else:
            # Not recognized
            pass