import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, 
    QListWidget, QTabWidget, QPlainTextEdit,
)
from PySide6.QtCore import Qt


class IDEMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Minimal IDE Prototype")
        self.resize(1200, 800)

        # Create the menu bar
        self._create_menu_bar()

        # Central area: QTabWidget as code editor placeholder.
        self.editor_tabs = QTabWidget()
        # Add a dummy tab for demonstration
        dummy_editor = QPlainTextEdit("print('Hello World')")
        self.editor_tabs.addTab(dummy_editor, "example.py")
        self.setCentralWidget(self.editor_tabs)

        #Left dock: File Explorer
        self.file_explorer_dock = QDockWidget("File Explorer", self)
        self.file_explorer_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        file_list = QListWidget()
        file_list.addItem("example.py")
        file_list.addItem("main.py")
        file_list.addItem("utils.py")
        self.file_explorer_dock.setWidget(file_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_explorer_dock)

        # Right dock: Outline/Symbol window
        self.outline_dock = QDockWidget("Outline", self)
        self.outline_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        outline_list = QListWidget()
        outline_list.addItem("Function: main()")
        outline_list.addItem("Class: ExampleClass")
        outline_list.addItem("def helper_function()")
        self.outline_dock.setWidget(outline_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.outline_dock)

        # Bottom dock: terminal
        self.terminal_dock = QDockWidget("Terminal", self)
        self.terminal_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        terminal = QPlainTextEdit()
        terminal.setPlainText(">>> ")
        self.terminal_dock.setWidget(terminal)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminal_dock)


    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Open")   #Placeholder action
        file_menu.addAction("Save")   #Placeholder action 
        file_menu.addAction("Exit")   #Placeholder action

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Cut")    #Placeholder action
        edit_menu.addAction("Copy")   #Placeholder action
        edit_menu.addAction("Paste")  #Placeholder action

        # Setings Menu.
        settings_menu = menu_bar.addMenu("Settings")
        settings_menu.addAction("Preferences") #Placeholder action 


  
def main():

    app = QApplication(sys.argv)
    window = IDEMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
