from PySide6.QtWidgets import QTabWidget, QPlainTextEdit
from PySide6.QtGui import QTextCursor, QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import Qt, QRegularExpression

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
        # Enable closable and movable tabs
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)

        dummy_editor = QPlainTextEdit("print('Hello World')")
        self._apply_highlighting(dummy_editor)
        dummy_editor.setProperty("file_path", None)
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
        file_name = file_path.split("/")[-1]
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
        self.removeTab(index)

    def _apply_highlighting(self, editor_widget):
        PythonHighlighter(editor_widget.document())
