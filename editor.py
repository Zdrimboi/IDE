from PySide6.QtWidgets import QTabWidget, QPlainTextEdit, QMenu, QApplication
from PySide6.QtGui import QTextCursor, QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import Qt, QRegularExpression, QPoint
import os

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("blue"))
        self.keyword_format.setFontWeight(QFont.Bold)

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("magenta"))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("green"))

        keywords = [
            "False", "class", "finally", "is", "return",
            "None", "continue", "for", "lambda", "try",
            "True", "def", "from", "nonlocal", "while",
            "and", "del", "global", "not", "with",
            "as", "elif", "if", "or", "yield",
            "assert", "else", "import", "pass",
            "break", "except", "in", "raise"
        ]

        self.keyword_patterns = [QRegularExpression(r"\b" + w + r"\b") for w in keywords]
        self.string_patterns = [QRegularExpression(r"\".*?\""), QRegularExpression(r"\'.*?\'")]
        self.comment_pattern = QRegularExpression(r"#[^\n]*")

    def highlightBlock(self, text):
        for pattern in self.keyword_patterns:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.keyword_format)

        for pattern in self.string_patterns:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.string_format)

        match_iterator = self.comment_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.comment_format)


class EditorTabs(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_tab_context_menu)

        dummy_editor = QPlainTextEdit("print('Hello World')")
        self._apply_highlighting(dummy_editor)
        dummy_editor.setProperty("file_path", None)
        dummy_editor.setProperty("pinned", False)  # Pinned state
        self.addTab(dummy_editor, "example.py")

    def open_file(self, file_path):
        for i in range(self.count()):
            editor = self.widget(i)
            if editor.property("file_path") == file_path:
                self.setCurrentIndex(i)
                return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            text = f"Error opening file:\n{e}"

        editor = QPlainTextEdit(text)
        self._apply_highlighting(editor)
        editor.setProperty("file_path", file_path)
        editor.setProperty("pinned", False)
        file_name = os.path.basename(file_path)
        self.addTab(editor, file_name)
        self.setCurrentWidget(editor)
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)

    def current_editor(self):
        return self.currentWidget()

    def current_file_path(self):
        editor = self.current_editor()
        if editor:
            return editor.property("file_path")
        return None

    def save_current_file(self):
        editor = self.current_editor()
        if editor is not None:
            file_path = editor.property("file_path")
            if file_path is not None:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(editor.toPlainText())
                except Exception as e:
                    print(f"Error saving file: {e}")

    def close_tab(self, index):
        editor = self.widget(index)
        if editor and not editor.property("pinned"):
            self.removeTab(index)

    def _apply_highlighting(self, editor_widget):
        PythonHighlighter(editor_widget.document())

    def _on_tab_context_menu(self, pos: QPoint):
        # Find which tab was clicked
        tab_index = self.tabBar().tabAt(pos)
        if tab_index < 0:
            return

        editor = self.widget(tab_index)
        file_path = editor.property("file_path")
        pinned = editor.property("pinned")

        menu = QMenu(self)

        close_all_action = menu.addAction("Close All")
        close_this_action = menu.addAction("Close This")
        pin_action = menu.addAction("Unpin" if pinned else "Pin")

        menu.addSeparator()

        open_in_file_explorer_action = menu.addAction("Open in File Explorer")
        open_file_location_action = menu.addAction("Open file location")
        copy_abs_path_action = menu.addAction("Copy absolute path")
        copy_rel_path_action = menu.addAction("Copy relative path")

        # Disable actions if file_path is None (dummy tab)
        if file_path is None:
            open_in_file_explorer_action.setEnabled(False)
            open_file_location_action.setEnabled(False)
            copy_abs_path_action.setEnabled(False)
            copy_rel_path_action.setEnabled(False)

        # Handle triggers
        action = menu.exec(self.mapToGlobal(pos))
        if action == close_all_action:
            self._close_all_tabs_except_pinned()
        elif action == close_this_action:
            # Close this tab if not pinned
            if not pinned:
                self.removeTab(tab_index)
        elif action == pin_action:
            # Toggle pinned state
            editor.setProperty("pinned", not pinned)
        elif action == open_in_file_explorer_action and file_path:
            self._open_in_internal_file_explorer(file_path)
        elif action == open_file_location_action and file_path:
            self._open_file_location(file_path)
        elif action == copy_abs_path_action and file_path:
            self._copy_to_clipboard(file_path)
        elif action == copy_rel_path_action and file_path:
            self._copy_relative_path(file_path)

    def _close_all_tabs_except_pinned(self):
        # Iterate and close all non-pinned tabs
        i = 0
        while i < self.count():
            editor = self.widget(i)
            if not editor.property("pinned"):
                self.removeTab(i)
            else:
                i += 1

    def _open_in_internal_file_explorer(self, file_path):
        # Show the file in the internal file explorer
        main_window = self.window()
        if hasattr(main_window, 'file_explorer_dock'):
            main_window.file_explorer_dock.show_file_in_explorer(file_path)

    def _open_file_location(self, file_path):
        # Open the containing folder in the system file explorer
        directory = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
        if os.path.isdir(directory):
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl.fromLocalFile(directory))

    def _copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def _copy_relative_path(self, file_path):
        main_window = self.window()
        if hasattr(main_window, 'file_explorer_dock'):
            root_path = main_window.file_explorer_dock.model.rootPath()
            relative = os.path.relpath(file_path, root_path)
            self._copy_to_clipboard(relative)
        else:
            self._copy_to_clipboard(file_path)  # fallback if no explorer available
