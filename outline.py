import os
import ast
import re
from PySide6.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor

class OutlineDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Outline", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Symbols")
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        self.setWidget(self.tree_widget)

        self.editor_tabs = None

    def set_editor_tabs(self, editor_tabs):
        self.editor_tabs = editor_tabs

    def refresh_outline(self):
        if not self.editor_tabs:
            return

        editor = self.editor_tabs.current_editor()
        if editor is None:
            self.tree_widget.clear()
            return

        file_path = editor.property("file_path")
        if not file_path:
            self.tree_widget.clear()
            return

        file_extension = os.path.splitext(file_path)[1].lower()
        file_content = editor.toPlainText()

        if file_extension == ".py":
            symbols = self._parse_python(file_content)
        elif file_extension == ".c":
            # Use our custom parser
            symbols = self._parse_c_custom(file_content)
        else:
            self.tree_widget.clear()
            return

        self._populate_tree(symbols)

    def _parse_python(self, source_code):
        # Use the built-in ast approach
        import ast
        symbols = []
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    symbols.append((f"class {node.name}", node.lineno))
                elif isinstance(node, ast.FunctionDef):
                    symbols.append((f"def {node.name}()", node.lineno))
        except Exception as e:
            print(f"Error parsing Python: {e}")
        return symbols

    def _parse_c_custom(self, source_code):
        """
        Our custom function for extracting #directives and function definitions.
        """
        symbols = []
        lines = source_code.splitlines()

        func_def_pattern = re.compile(
            r"""^
               ([A-Za-z_][A-Za-z0-9_\*\s]*?)   # return type + pointer symbols
               \s+([A-Za-z_][A-Za-z0-9_]*)    # function name
               \s*\([^)]*\)\s*\{
               """,
            re.VERBOSE
        )

        for i, line in enumerate(lines, start=1):
            striped = line.strip()
            if striped.startswith('#'):
                # #include, #define, #if, etc.
                symbols.append((striped, i))
                continue

            match = func_def_pattern.match(striped)
            if match:
                return_type = match.group(1).strip()
                func_name = match.group(2).strip()
                symbols.append((f"function {func_name}()", i))

        return symbols

    def _populate_tree(self, symbols):
        self.tree_widget.clear()
        for name, line_num in symbols:
            item = QTreeWidgetItem(self.tree_widget)
            item.setText(0, name)
            item.setData(0, Qt.UserRole, line_num)
        self.tree_widget.expandAll()

    def _on_item_clicked(self, item, column):
        line_num = item.data(0, Qt.UserRole)
        if line_num and self.editor_tabs:
            editor = self.editor_tabs.current_editor()
            if editor:
                self._go_to_line(editor, line_num)

    def _go_to_line(self, editor, line):
        text_cursor = editor.textCursor()
        # Move to the start of the document
        text_cursor.movePosition(QTextCursor.Start)

        # Move down (line - 1) lines
        for _ in range(line - 1):
            text_cursor.movePosition(QTextCursor.Down)

        editor.setTextCursor(text_cursor)
        
        # Make sure the editor gets focus so the blinking cursor is visible
        editor.setFocus()
        
        # Optionally ensure the new cursor position is scrolled into view
        editor.ensureCursorVisible()

