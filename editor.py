from PySide6.QtWidgets import QTabWidget, QPlainTextEdit
from PySide6.QtGui import QTextCursor

class EditorTabs(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Add a dummy file to start with
        dummy_editor = QPlainTextEdit("print('Hello World')")
        self.addTab(dummy_editor, "example.py")

    def open_file(self, file_path):
        # Check if file is already open
        for i in range(self.count()):
            editor = self.widget(i)
            if editor.property("file_path") == file_path:
                # File already open, just switch to that tab
                self.setCurrentIndex(i)
                return

        # If not, open the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            # In a production environment, handle error (show message, etc.)
            text = f"Error opening file:\n{e}"

        editor = QPlainTextEdit(text)
        editor.setProperty("file_path", file_path)

        # Extract just the filename from the path
        file_name = file_path.split("/")[-1]
        self.addTab(editor, file_name)
        self.setCurrentWidget(editor)
        
        # Move cursor to start of file
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)
