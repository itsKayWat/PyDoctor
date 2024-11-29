import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, 
                            QPushButton, QVBoxLayout, QWidget,
                            QProgressBar, QMessageBox, QSystemTrayIcon,
                            QMenu, QTextEdit)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont, QColor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.click_count = 0
        self.initUI()
        self.setupSystemTray()
        
    def initUI(self):
        self.setWindowTitle("PyQt6 Test")
        self.setGeometry(100, 100, 500, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create and style the main label
        self.main_label = QLabel("PyQt6 is working!", self)
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #2c3e50;
                font-weight: bold;
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        
        # Add status label
        self.status_label = QLabel("System Status: Ready", self)
        self.status_label.setStyleSheet("color: #27ae60; font-size: 14px;")
        
        # Add progress bar
        self.progress = QProgressBar(self)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 10px;
            }
        """)
        self.progress.setValue(0)
        
        # Add test button
        self.test_button = QPushButton("Test Button", self)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border: 2px solid #2980b9;
            }
            QPushButton:pressed {
                background-color: #2574a9;
            }
        """)
        self.test_button.clicked.connect(self.button_clicked)
        
        # Add debug text area
        self.debug_area = QTextEdit(self)
        self.debug_area.setReadOnly(True)
        self.debug_area.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
                font-family: Consolas, Monaco, monospace;
            }
        """)
        self.debug_area.setMaximumHeight(100)
        
        # Add reset button
        reset_button = QPushButton("Reset", self)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        reset_button.clicked.connect(self.reset_application)
        
        # Add widgets to layout
        layout.addWidget(self.main_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.test_button)
        layout.addWidget(self.debug_area)
        layout.addWidget(reset_button)
        
        # Setup timer for progress bar animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        
        # Initialize status bar
        self.statusBar().showMessage("Application ready")
        
    def setupSystemTray(self):
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip('PyQt6 Test Application')
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        hide_action = tray_menu.addAction("Hide")
        hide_action.triggered.connect(self.hide)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def button_clicked(self):
        self.click_count += 1
        self.debug_area.append(f"Button clicked {self.click_count} times")
        self.status_label.setText(f"Processing click {self.click_count}...")
        self.status_label.setStyleSheet("color: #e67e22; font-size: 14px;")
        
        # Start progress animation
        self.progress.setValue(0)
        self.timer.start(50)
        
        # Show notification
        self.tray_icon.showMessage(
            "Button Clicked",
            f"Button has been clicked {self.click_count} times",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def update_progress(self):
        current = self.progress.value()
        if current < 100:
            self.progress.setValue(current + 5)
        else:
            self.timer.stop()
            self.status_label.setText("Operation completed!")
            self.status_label.setStyleSheet("color: #27ae60; font-size: 14px;")
    
    def reset_application(self):
        reply = QMessageBox.question(
            self, 'Reset Confirmation',
            'Are you sure you want to reset the application?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.click_count = 0
            self.progress.setValue(0)
            self.debug_area.clear()
            self.status_label.setText("System Status: Ready")
            self.status_label.setStyleSheet("color: #27ae60; font-size: 14px;")
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Application Minimized",
            "Application is still running in the system tray",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide style sheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f6fa;
        }
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QMessageBox {
            background-color: #f5f6fa;
        }
        QMessageBox QPushButton {
            padding: 5px 15px;
            border-radius: 3px;
            background-color: #3498db;
            color: white;
        }
    """)
    
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
