import os
import platform
from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QPlainTextEdit, QLineEdit
from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QTextCursor

class TerminalDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Terminal", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.output_view = QPlainTextEdit()
        self.output_view.setReadOnly(True)
        self.output_view.appendPlainText(">>> ")

        self.input_line = QLineEdit()
        self.input_line.returnPressed.connect(self.run_command)

        layout.addWidget(self.output_view)
        layout.addWidget(self.input_line)
        self.setWidget(container)

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.on_read_output)
        self.process.finished.connect(self.on_command_finished)

        self.shell_command = self._detect_shell_command()

    def _detect_shell_command(self):
        if platform.system().lower().startswith('win'):
            return ["cmd.exe", "/C"]
        else:
            return ["/bin/sh", "-c"]

    def run_command(self):
        command = self.input_line.text().strip()
        if not command:
            return
        self.input_line.clear()
        self.execute_command(command)

    def execute_command(self, command: str):
        self.output_view.moveCursor(QTextCursor.End)
        self.output_view.insertPlainText("> " + command + "\n")
        self.process.start(self.shell_command[0], self.shell_command[1:] + [command])

    def on_read_output(self):
        data = self.process.readAllStandardOutput().data().decode(errors='replace')
        self.output_view.moveCursor(QTextCursor.End)
        self.output_view.insertPlainText(data)

    def on_command_finished(self):
        self.output_view.moveCursor(QTextCursor.End)
        self.output_view.insertPlainText(">>> ")
        self.output_view.verticalScrollBar().setValue(self.output_view.verticalScrollBar().maximum())

    def reset_terminal(self):
        """Kill any running process, clear output, and re-initialize QProcess."""
        # If a process is running, kill it
        if self.process.state() == QProcess.Running:
            self.process.kill()
            self.process.waitForFinished(1000)

        # Clear the output
        self.output_view.clear()

        # Re-create the prompt
        self.output_view.appendPlainText(">>> ")
        self.input_line.clear()

        # Re-init QProcess connections
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.on_read_output)
        self.process.finished.connect(self.on_command_finished)
        # shell_command remains the same (no need to reset)
