from PySide6.QtWidgets import QTabWidget, QPlainTextEdit, QMenu, QApplication
from PySide6.QtGui import QTextCursor, QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import Qt, QPoint
import os
import re
import tokenize
import io

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self._init_formats()

    def _init_formats(self):
        """Initialize QTextCharFormat objects for different token types."""
        self.formats = {}

        # Example color scheme
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))  # Blue
        keyword_format.setFontWeight(QFont.Bold)
        self.formats['keyword'] = keyword_format

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#FF00FF"))  # Magenta
        self.formats['string'] = string_format

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#008000"))  # Green
        self.formats['comment'] = comment_format

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FF8000"))  # Orange
        self.formats['number'] = number_format

        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#800080"))  # Purple
        self.formats['builtin'] = builtin_format

        default_format = QTextCharFormat()
        self.formats['default'] = default_format

        # A minimal set of Python keywords (you can expand)
        self.keywords = {
            "False", "class", "finally", "is", "return", 
            "None", "continue", "for", "lambda", "try",
            "True", "def", "from", "nonlocal", "while",
            "and", "del", "global", "not", "with",
            "as", "elif", "if", "or", "yield",
            "assert", "else", "import", "pass",
            "break", "except", "in", "raise"
        }

        # Some builtins
        self.builtins = {
            "print", "range", "len", "dict", "list", "int", "float", 
            "str", "bool", "set", "tuple", "input", "open"
        }

    def highlightBlock(self, text):
        """Re-implemented from QSyntaxHighlighter. We highlight per line, 
           but tokenize needs the entire document for context (multiline strings, etc.).
        """
        # We'll store line results in a buffer for later.
        self.setFormat(0, len(text), self.formats['default'])

        # We only highlight per line. But we need full doc to tokenize properly.
        # So let's do: if we have a multi-line doc, we'll highlight everything once,
        # storing results in an internal structure, and apply them line by line.
        if self.currentBlock().blockNumber() == 0:
            # This means we're at the first line, so let's do a full re-tokenize
            self._all_formats = self._parse_and_format_entire_doc()

        # Now apply any tokens that fall within this line’s range
        block_num = self.currentBlock().blockNumber()
        if block_num in self._all_formats:
            for (start, length, fmt) in self._all_formats[block_num]:
                self.setFormat(start, length, fmt)

    def _parse_and_format_entire_doc(self):
        doc_text = self.document().toPlainText()
        results = {}  # line_index -> list of (start_col, length, QTextCharFormat)
        
        tokens_list = list(tokenize.generate_tokens(io.StringIO(doc_text).readline))
        
        # We'll do a single pass to assign each token a format initially
        # as you do now:
        basic_formats = []
        for i, tok in enumerate(tokens_list):
            ttype, tstring, start, end, _ = tok
            start_line, start_col = start
            end_line, end_col = end

            fmt = self._choose_format(ttype, tstring)
            
            # We store the base info and also keep them in a list for the second pass
            basic_formats.append((i, ttype, tstring, start_line, start_col, end_line, end_col, fmt))

        # === SECOND PASS: detect function calls & arguments ===
        i = 0
        while i < len(basic_formats) - 1:
            (idx, ttype, tstring, start_line, start_col,
             end_line, end_col, fmt) = basic_formats[i]
            
            # If we see NAME followed by OP "(" => treat NAME as function
            import token
            if ttype == token.NAME and (i+1 < len(basic_formats)):
                next_ttype = basic_formats[i+1][1]
                next_tstring = basic_formats[i+1][2]
                if next_ttype == token.OP and next_tstring == '(':
                    # Mark this name as "function" color
                    fmt = self.formats['builtin']  # or define self.formats['function_call'] separately
                    # update the list record
                    basic_formats[i] = (idx, ttype, tstring, start_line, start_col,
                                        end_line, end_col, fmt)
                    
                    # Now we can optionally parse arguments up to the matching ")"
                    # We'll skip real bracket matching for brevity, but let's do a naive approach:
                    # track parentheses nesting
                    paren_depth = 1
                    j = i+2
                    while j < len(basic_formats) and paren_depth > 0:
                        j_tok = basic_formats[j]
                        j_ttype = j_tok[1]
                        j_tstring = j_tok[2]
                        if j_ttype == token.OP and j_tstring == '(':
                            paren_depth += 1
                        elif j_ttype == token.OP and j_tstring == ')':
                            paren_depth -= 1
                        else:
                            # If we want arguments in a special color, e.g. if it's a NAME
                            if paren_depth == 1 and j_ttype == token.NAME:
                                # color it as argument
                                # We'll need to re-pack the record with a new format
                                j_record = list(j_tok)
                                j_record[-1] = self.formats['builtin']  # or self.formats['argument']
                                basic_formats[j] = tuple(j_record)
                        j += 1
                    # i can jump to j-1 to skip scanning these tokens again
                    i = j - 1
            i += 1

        # Now that we have final formats, let's break them into line-based segments
        for (idx, ttype, tstring, start_line, start_col, end_line, end_col, fmt) in basic_formats:
            # For each line from start_line to end_line, store highlight
            for line_no in range(start_line-1, end_line):
                if line_no not in results:
                    results[line_no] = []
                
                if start_line != end_line:
                    # multiline token
                    # naive splitting code as you have now
                    if line_no == (start_line-1):
                        length = len(doc_text.splitlines()[line_no]) - start_col
                        results[line_no].append((start_col, length, fmt))
                    elif line_no == (end_line-1):
                        length = end_col
                        results[line_no].append((0, length, fmt))
                    else:
                        line_len = len(doc_text.splitlines()[line_no])
                        results[line_no].append((0, line_len, fmt))
                else:
                    length = end_col - start_col
                    results[line_no].append((start_col, length, fmt))

        return results

    def _choose_format(self, ttype, tstring):
        """Decide which format to apply based on token type or content."""
        import token
        if ttype == token.COMMENT:
            return self.formats['comment']
        elif ttype == token.STRING:
            return self.formats['string']
        elif ttype == token.NUMBER:
            return self.formats['number']
        elif ttype == token.NAME:
            # Might be a keyword, builtin, or normal identifier
            if tstring in self.keywords:
                return self.formats['keyword']
            elif tstring in self.builtins:
                return self.formats['builtin']
            else:
                return self.formats['default']
        else:
            # default
            return self.formats['default']

class CHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self._init_formats()
        self._init_patterns()

    def _init_formats(self):
        """Create and store QTextCharFormat objects for each token type."""
        self.formats = {}

        # 1) Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))  # Blue
        keyword_format.setFontWeight(QFont.Bold)
        self.formats["keyword"] = keyword_format

        # 2) Types
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#008080"))  # Teal
        type_format.setFontWeight(QFont.Bold)
        self.formats["type"] = type_format

        # 3) Function (definition or call)
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#800080"))  # Purple
        function_format.setFontWeight(QFont.Bold)
        self.formats["function"] = function_format

        # 4) Arguments (naive)
        arg_format = QTextCharFormat()
        arg_format.setForeground(QColor("#006666"))  # Dark teal
        self.formats["argument"] = arg_format

        # 5) Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FF8000"))  # Orange
        self.formats["number"] = number_format

        # 6) Identifiers (generic)
        identifier_format = QTextCharFormat()
        identifier_format.setForeground(QColor("#000000"))  # Black
        self.formats["identifier"] = identifier_format

        # 7) String
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#FF00FF"))  # Magenta
        self.formats["string"] = string_format

        # 8) Single-line comment
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#008000"))  # Green
        self.formats["comment"] = comment_format

        # 9) Preprocessor directives
        directive_format = QTextCharFormat()
        directive_format.setForeground(QColor("#008000"))  # Green
        directive_format.setFontWeight(QFont.Bold)
        self.formats["directive"] = directive_format

        # Default
        default_format = QTextCharFormat()
        self.formats["default"] = default_format

        # Known C keywords
        self.keywords = {
            "auto","break","case","char","const","continue","default","do","double",
            "else","enum","extern","float","for","goto","if","inline","int","long",
            "register","restrict","return","short","signed","sizeof","static","struct",
            "switch","typedef","union","unsigned","void","volatile","while"
        }

        # Built-in types or synonyms
        self.types = {
            "int","float","double","char","long","short","signed","unsigned","void"
        }

    def _init_patterns(self):
        """Compile all the regex patterns we will use."""
        # Preprocessor directives (start of line with #)
        # e.g. "#include <stdio.h>"
        self.directive_pattern = re.compile(r'^\s*#\s*\w+.*', re.MULTILINE)

        # Single-line comment
        self.single_comment_pattern = re.compile(r'//[^\n]*')

        # String (naive)
        self.string_pattern = re.compile(r'"[^"\\]*(\\.[^"\\]*)*"')

        # Numbers
        # Matches integers, floats, but very naive. 
        self.number_pattern = re.compile(r'\b\d+(\.\d+)?\b')

        # Keywords (word boundary)
        kw_alts = "|".join(sorted(self.keywords, key=len, reverse=True))
        self.keyword_pattern = re.compile(r'\b(' + kw_alts + r')\b')

        # Types (similarly, we can highlight them distinctly)
        type_alts = "|".join(sorted(self.types, key=len, reverse=True))
        self.type_pattern = re.compile(r'\b(' + type_alts + r')\b')

        # Function calls (simple approach):
        # e.g. "myFunc(...)" capturing "myFunc"
        # We'll color the name "myFunc" as a function. 
        # This also might catch "if (...)" incorrectly if not careful, but let's keep it naive
        self.function_call_pattern = re.compile(r'\b([A-Za-z_]\w*)\s*\(')

        # For arguments, we do something naive: inside parentheses after a function,
        # highlight [A-Za-z_]\w* as an argument. This is extremely naive.
        self.argument_pattern = re.compile(r'\((.*?)\)')

    def highlightBlock(self, text):
        """Highlight a single line of text. Also handle multiline comments with block states."""
        self.setFormat(0, len(text), self.formats["default"])

        # 1) Preprocessor directives
        for match in self.directive_pattern.finditer(text):
            start, end = match.span()
            self.setFormat(start, end - start, self.formats["directive"])

        # 2) Single-line comments
        for match in self.single_comment_pattern.finditer(text):
            start, end = match.span()
            self.setFormat(start, end - start, self.formats["comment"])

        # 3) Strings
        for match in self.string_pattern.finditer(text):
            start, end = match.span()
            self.setFormat(start, end - start, self.formats["string"])

        # 4) Numbers
        for match in self.number_pattern.finditer(text):
            start, end = match.span()
            self.setFormat(start, end - start, self.formats["number"])

        # 5) Keywords
        for match in self.keyword_pattern.finditer(text):
            start, end = match.span(1)
            self.setFormat(start, end - start, self.formats["keyword"])

        # 6) Types
        for match in self.type_pattern.finditer(text):
            start, end = match.span(1)
            self.setFormat(start, end - start, self.formats["type"])

        # 7) Function calls (naive)
        # We'll highlight the function name portion
        for match in self.function_call_pattern.finditer(text):
            func_name_start, func_name_end = match.span(1)
            # check if it's not a keyword like 'if'
            # but let's keep it simple
            self.setFormat(func_name_start, func_name_end - func_name_start, self.formats["function"])

            # Now, if you want to highlight arguments: we can do a second pattern on the substring
            # that starts after '(' up to the matching ')'. This is naive if parentheses are nested
            paren_start = match.end() - 1  # position of '('
            # find the matching ')'. We'll do a naive approach scanning forward
            end_paren_index = text.find(')', paren_start)
            if end_paren_index != -1:
                # everything inside parentheses is arguments
                arg_text = text[paren_start+1:end_paren_index]
                # We can highlight each identifier as an argument
                # e.g. for something like: (x, y+1, struct Foo* bar)
                # let's do a simplistic approach with a regex
                arg_id_pattern = re.compile(r'\b[A-Za-z_]\w*\b')
                for arg_match in arg_id_pattern.finditer(arg_text):
                    arg_start = paren_start + 1 + arg_match.start()
                    arg_len = arg_match.end() - arg_match.start()
                    self.setFormat(arg_start, arg_len, self.formats["argument"])

        # 8) Multiline comments
        self._highlight_multiline_comments(text)

    def _highlight_multiline_comments(self, text):
        """
        Use block states to handle /* ... */ across multiple lines.
        We'll store 1 if we're inside a comment, -1 if not.
        """
        in_comment = (self.previousBlockState() == 1)
        start_idx = 0

        if in_comment:
            close_idx = text.find("*/", start_idx)
            if close_idx == -1:
                self.setFormat(0, len(text), self.formats["comment"])
                self.setCurrentBlockState(1)
                return
            else:
                self.setFormat(0, close_idx+2, self.formats["comment"])
                start_idx = close_idx+2
                in_comment = False

        while True:
            open_idx = text.find("/*", start_idx)
            if open_idx == -1:
                break
            close_idx = text.find("*/", open_idx + 2)
            if close_idx == -1:
                # highlight until end of line
                self.setFormat(open_idx, len(text) - open_idx, self.formats["comment"])
                self.setCurrentBlockState(1)
                return
            else:
                self.setFormat(open_idx, close_idx+2 - open_idx, self.formats["comment"])
                start_idx = close_idx+2

        if not in_comment:
            self.setCurrentBlockState(-1)

def _configure_editor(editor: QPlainTextEdit):
    # Use the editor's current font metrics to compute how wide one space is:
    space_width = editor.fontMetrics().horizontalAdvance(' ')
    # We want 4 "spaces"
    editor.setTabStopDistance(8 * space_width)

class EditorTabs(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_tab_context_menu)


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
        _configure_editor(editor)
        # Set the file_path BEFORE highlighting
        editor.setProperty("file_path", file_path)
        editor.setProperty("pinned", False)

        file_name = os.path.basename(file_path)
        self.addTab(editor, file_name)
        self.setCurrentWidget(editor)

        # Move cursor to start
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)

        # Now apply highlighting with a known path
        self._apply_highlighting(editor, file_path)

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

    def _apply_highlighting(self, editor_widget, file_path):
        """Choose which highlighter based on file extension."""
        extension = os.path.splitext(file_path)[1].lower()
        if extension == ".py":
            PythonHighlighter(editor_widget.document())
        elif extension == ".c":
            CHighlighter(editor_widget.document())
        else:
            # You can pick a default highlighter or do nothing
            pass


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
