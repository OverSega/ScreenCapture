from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QDialog, QCheckBox, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QFont, QPixmap, QIcon
import config
import copy


APP_FONT = QFont("Segoe UI", 10)


class KeyButton(QPushButton):
    """Кнопка для назначения клавиши."""
    
    key_assigned = pyqtSignal(str)
    assigning_started = pyqtSignal()
    assigning_stopped = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(220, 38)
        self.setText("Нажмите клавишу...")
        self.current_key = ""
        self.waiting_for_key = False
        
        self.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                border: 2px solid #d0d0d0;
                border-radius: 6px;
                font-size: 14px;
                font-family: 'Segoe UI';
                background-color: #fafafa;
                text-align: left;
                color: #333;
            }
            QPushButton:hover {
                border-color: #2196F3;
                background-color: #f0f8ff;
            }
        """)
        
        self.clicked.connect(self.start_waiting)
    
    def start_waiting(self):
        self.waiting_for_key = True
        self.setText("Нажмите клавишу...")
        self.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                border: 2px solid #2196F3;
                border-radius: 6px;
                font-size: 14px;
                font-family: 'Segoe UI';
                background-color: #E3F2FD;
                text-align: left;
                color: #1565C0;
            }
        """)
        self.setFocus()
        self.assigning_started.emit()
    
    def focusOutEvent(self, event):
        if self.waiting_for_key:
            self.waiting_for_key = False
            self.assigning_stopped.emit()
            if not self.current_key:
                self.setText("Нажмите клавишу...")
                self.setStyleSheet("""
                    QPushButton {
                        padding: 8px 15px;
                        border: 2px solid #d0d0d0;
                        border-radius: 6px;
                        font-size: 14px;
                        font-family: 'Segoe UI';
                        background-color: #fafafa;
                        text-align: left;
                        color: #333;
                    }
                    QPushButton:hover {
                        border-color: #2196F3;
                        background-color: #f0f8ff;
                    }
                """)
        super().focusOutEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        if not self.waiting_for_key:
            super().keyPressEvent(event)
            return
        
        if event.key() in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            return
        
        key_name = self._get_key_name(event.key())
        if not key_name:
            return
        
        self.current_key = key_name
        self.setText(key_name)
        self.waiting_for_key = False
        self.assigning_stopped.emit()
        
        self.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                font-size: 14px;
                font-family: 'Segoe UI';
                background-color: #E8F5E9;
                text-align: left;
                color: #2E7D32;
                font-weight: bold;
            }
        """)
        
        self.key_assigned.emit(key_name)
    
    def _get_key_name(self, key):
        key_map = {
            Qt.Key_F1: "F1", Qt.Key_F2: "F2", Qt.Key_F3: "F3", Qt.Key_F4: "F4",
            Qt.Key_F5: "F5", Qt.Key_F6: "F6", Qt.Key_F7: "F7", Qt.Key_F8: "F8",
            Qt.Key_F9: "F9", Qt.Key_F10: "F10", Qt.Key_F11: "F11", Qt.Key_F12: "F12",
            Qt.Key_Escape: "Esc", Qt.Key_Return: "Enter", Qt.Key_Enter: "Enter",
            Qt.Key_Backspace: "Backspace", Qt.Key_Delete: "Delete",
            Qt.Key_Space: "Space", Qt.Key_Tab: "Tab",
            Qt.Key_Print: "PrintScreen", Qt.Key_Insert: "Insert",
            Qt.Key_Home: "Home", Qt.Key_End: "End",
            Qt.Key_PageUp: "PageUp", Qt.Key_PageDown: "PageDown",
            Qt.Key_Up: "Up", Qt.Key_Down: "Down", Qt.Key_Left: "Left", Qt.Key_Right: "Right",
            Qt.Key_0: "0", Qt.Key_1: "1", Qt.Key_2: "2", Qt.Key_3: "3", Qt.Key_4: "4",
            Qt.Key_5: "5", Qt.Key_6: "6", Qt.Key_7: "7", Qt.Key_8: "8", Qt.Key_9: "9",
            Qt.Key_A: "A", Qt.Key_B: "B", Qt.Key_C: "C", Qt.Key_D: "D", Qt.Key_E: "E",
            Qt.Key_F: "F", Qt.Key_G: "G", Qt.Key_H: "H", Qt.Key_I: "I", Qt.Key_J: "J",
            Qt.Key_K: "K", Qt.Key_L: "L", Qt.Key_M: "M", Qt.Key_N: "N", Qt.Key_O: "O",
            Qt.Key_P: "P", Qt.Key_Q: "Q", Qt.Key_R: "R", Qt.Key_S: "S", Qt.Key_T: "T",
            Qt.Key_U: "U", Qt.Key_V: "V", Qt.Key_W: "W", Qt.Key_X: "X", Qt.Key_Y: "Y",
            Qt.Key_Z: "Z",
        }
        return key_map.get(key, "")
    
    def clear_key(self):
        self.current_key = ""
        self.setText("Нажмите клавишу...")
        self.waiting_for_key = False
        self.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                border: 2px solid #d0d0d0;
                border-radius: 6px;
                font-size: 14px;
                font-family: 'Segoe UI';
                background-color: #fafafa;
                text-align: left;
                color: #333;
            }
            QPushButton:hover {
                border-color: #2196F3;
                background-color: #f0f8ff;
            }
        """)


class SettingsWindow(QWidget):
    """Окно настроек горячих клавиш."""
    
    close_to_tray = pyqtSignal()
    close_app = pyqtSignal()
    start_assigning = pyqtSignal()
    stop_assigning = pyqtSignal()
    settings_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.config = config.load_config()
        self.original_config = copy.deepcopy(self.config)
        self.pulse_timer = None
        self.pulse_state = 0
        self.init_ui()
        self.load_settings()
        self.check_unsaved_changes()
    
    def init_ui(self):
        self.setWindowTitle("ScreenCapture")
        self.setFixedSize(550, 520)
        self.setFont(APP_FONT)
        
        try:
            pixmap = QPixmap("icon.png")
            pixmap = pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setWindowIcon(QIcon(pixmap))
        except Exception as e:
            print(f"Ошибка установки иконки окна: {e}")
        
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI';
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(35, 30, 35, 25)
        
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        try:
            pixmap = QPixmap("icon.png")
            pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        except:
            pass
        layout.addWidget(icon_label)
        
        app_title = QLabel("ScreenCapture")
        app_title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        app_title.setStyleSheet("color: #222; margin-bottom: 5px;")
        app_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_title)
        
        subtitle = QLabel("Настройки горячих клавиш")
        subtitle.setFont(QFont("Segoe UI", 11, QFont.Bold))
        subtitle.setStyleSheet("color: #000000; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        row1 = QHBoxLayout()
        label1 = QLabel("Выделение области:")
        label1.setFont(QFont("Segoe UI", 11))
        label1.setFixedWidth(180)
        row1.addWidget(label1)
        self.screenshot_key = KeyButton()
        self.screenshot_key.key_assigned.connect(lambda: self.on_key_changed())
        self.screenshot_key.assigning_started.connect(self.start_assigning.emit)
        self.screenshot_key.assigning_stopped.connect(self.stop_assigning.emit)
        row1.addWidget(self.screenshot_key)
        row1.addStretch()
        layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        label2 = QLabel("Отправка:")
        label2.setFont(QFont("Segoe UI", 11))
        label2.setFixedWidth(180)
        row2.addWidget(label2)
        self.send_key = KeyButton()
        self.send_key.key_assigned.connect(lambda: self.on_key_changed())
        self.send_key.assigning_started.connect(self.start_assigning.emit)
        self.send_key.assigning_stopped.connect(self.stop_assigning.emit)
        row2.addWidget(self.send_key)
        row2.addStretch()
        layout.addLayout(row2)
        
        layout.addSpacing(10)
        separator = QLabel("────────────────────────────────────────────")
        separator.setStyleSheet("color: #bbb; font-size: 11px;")
        layout.addWidget(separator)
        layout.addSpacing(5)
        
        extra_title = QLabel("Дополнительно:")
        extra_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        extra_title.setStyleSheet("color: #666;")
        layout.addWidget(extra_title)
        
        row3 = QHBoxLayout()
        label3 = QLabel("Весь экран:")
        label3.setFont(QFont("Segoe UI", 11))
        label3.setFixedWidth(180)
        row3.addWidget(label3)
        self.fullscreen_key = KeyButton()
        self.fullscreen_key.key_assigned.connect(lambda: self.on_key_changed())
        self.fullscreen_key.assigning_started.connect(self.start_assigning.emit)
        self.fullscreen_key.assigning_stopped.connect(self.stop_assigning.emit)
        row3.addWidget(self.fullscreen_key)
        row3.addStretch()
        layout.addLayout(row3)
        
        layout.addSpacing(8)
        self.clear_checkbox = QCheckBox("Очищать буфер обмена после отправки скриншота")
        self.clear_checkbox.setChecked(self.config.get("clear_after_send", True))
        self.clear_checkbox.stateChanged.connect(lambda: self.on_key_changed())
        self.clear_checkbox.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self.clear_checkbox)
        
        self.hint_label = QLabel("⚠ Назначьте клавиши перед работой.")
        self.hint_label.setFont(QFont("Segoe UI", 11))
        self.hint_label.setStyleSheet("color: #FF9800; margin-top: 12px;")
        layout.addWidget(self.hint_label)
        
        self.unsaved_label = QLabel("● Изменения не сохранены")
        self.unsaved_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.unsaved_label.setStyleSheet("color: #f44336; margin-top: 8px;")
        self.unsaved_label.hide()
        layout.addWidget(self.unsaved_label)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.reset_btn = QPushButton("Сбросить")
        self.reset_btn.setFixedSize(130, 40)
        self.reset_btn.setFont(QFont("Segoe UI", 11))
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #d32f2f; }
            QPushButton:pressed { background-color: #b71c1c; }
        """)
        self.reset_btn.clicked.connect(self.reset_settings)
        btn_layout.addWidget(self.reset_btn)
        
        btn_layout.addSpacing(20)
        
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setFixedSize(130, 40)
        self.save_btn.setFont(QFont("Segoe UI", 11))
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #388e3c; }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.start_pulsation()
    
    def load_settings(self):
        if config.get_hotkey(self.config, "screenshot"):
            self.screenshot_key.current_key = config.get_hotkey(self.config, "screenshot")
            self.screenshot_key.setText(self.screenshot_key.current_key)
        
        if config.get_hotkey(self.config, "send"):
            self.send_key.current_key = config.get_hotkey(self.config, "send")
            self.send_key.setText(self.send_key.current_key)
        
        if config.get_hotkey(self.config, "fullscreen"):
            self.fullscreen_key.current_key = config.get_hotkey(self.config, "fullscreen")
            self.fullscreen_key.setText(self.fullscreen_key.current_key)
        
        self.clear_checkbox.setChecked(self.config.get("clear_after_send", True))
        self.check_all_assigned()
    
    def on_key_changed(self):
        self.check_unsaved_changes()
        self.check_all_assigned()
    
    def check_unsaved_changes(self):
        current = {
            "hotkeys": {
                "screenshot": self.screenshot_key.current_key,
                "send": self.send_key.current_key,
                "fullscreen": self.fullscreen_key.current_key
            },
            "clear_after_send": self.clear_checkbox.isChecked()
        }
        
        original = {
            "hotkeys": self.original_config.get("hotkeys", {}),
            "clear_after_send": self.original_config.get("clear_after_send", True)
        }
        
        has_changes = (current != original)
        
        if has_changes:
            self.unsaved_label.show()
        else:
            self.unsaved_label.hide()
    
    def start_pulsation(self):
        self.pulse_state = 0
        if self.pulse_timer:
            self.pulse_timer.stop()
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_fields)
        self.pulse_timer.start(600)
    
    def pulse_fields(self):
        self.pulse_state = 1 - self.pulse_state
        color = "#FF9800" if self.pulse_state else "#d0d0d0"
        
        fields = [self.screenshot_key, self.send_key, self.fullscreen_key]
        for field in fields:
            if not field.current_key:
                field.setStyleSheet(f"""
                    QPushButton {{
                        padding: 8px 15px;
                        border: 2px solid {color};
                        border-radius: 6px;
                        font-size: 14px;
                        font-family: 'Segoe UI';
                        background-color: #fafafa;
                        text-align: left;
                        color: #333;
                    }}
                """)
    
    def check_all_assigned(self):
        if self.screenshot_key.current_key and self.send_key.current_key:
            self.hint_label.hide()
            if self.pulse_timer:
                self.pulse_timer.stop()
        else:
            self.hint_label.show()
            if self.pulse_timer and not self.pulse_timer.isActive():
                self.pulse_timer.start(600)
    
    def reset_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Сбросить настройки")
        dialog.setFixedSize(380, 130)
        dialog.setFont(APP_FONT)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setStyleSheet("QDialog { background-color: white; } QLabel { font-size: 13px; color: #333; }")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 15)
        layout.addWidget(QLabel("Очистить все назначенные клавиши?"))
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        yes_btn = QPushButton("Да")
        yes_btn.setFixedSize(90, 32)
        yes_btn.setFont(QFont("Segoe UI", 10))
        yes_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; border: none; border-radius: 5px; } QPushButton:hover { background-color: #d32f2f; }")
        yes_btn.clicked.connect(lambda: self.confirm_reset(dialog))
        btn_layout.addWidget(yes_btn)
        
        no_btn = QPushButton("Нет")
        no_btn.setFixedSize(90, 32)
        no_btn.setFont(QFont("Segoe UI", 10))
        no_btn.setStyleSheet("QPushButton { background-color: #e0e0e0; color: #333; border: none; border-radius: 5px; } QPushButton:hover { background-color: #bdbdbd; }")
        no_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(no_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def confirm_reset(self, dialog):
        dialog.accept()
        self.screenshot_key.clear_key()
        self.send_key.clear_key()
        self.fullscreen_key.clear_key()
        self.clear_checkbox.setChecked(True)
        self.hint_label.show()
        self.start_pulsation()
        self.check_unsaved_changes()
    
    def save_settings(self):
        if not self.screenshot_key.current_key or not self.send_key.current_key:
            self.show_error("Необходимо назначить клавиши для 'Выделение области' и 'Отправка'.")
            return
        
        keys = [
            self.screenshot_key.current_key,
            self.send_key.current_key,
            self.fullscreen_key.current_key
        ]
        keys = [k for k in keys if k]
        
        if len(keys) != len(set(keys)):
            self.show_error("Клавиши не должны повторяться. Проверьте назначения.")
            return
        
        config.set_hotkey(self.config, "screenshot", self.screenshot_key.current_key)
        config.set_hotkey(self.config, "send", self.send_key.current_key)
        config.set_hotkey(self.config, "fullscreen", self.fullscreen_key.current_key)
        self.config["clear_after_send"] = self.clear_checkbox.isChecked()
        self.config["first_run"] = False
        config.save_config(self.config)
        
        self.original_config = copy.deepcopy(self.config)
        self.check_unsaved_changes()
        
        self.settings_saved.emit()
        
        self.show_success("Настройки сохранены! Программа готова к работе.")
    
    def show_error(self, message):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ошибка")
        dialog.setFixedSize(400, 130)
        dialog.setFont(APP_FONT)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setStyleSheet("QDialog { background-color: white; } QLabel { font-size: 13px; color: #333; }")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 15)
        layout.addWidget(QLabel(message))
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setFixedSize(90, 32)
        ok_btn.setFont(QFont("Segoe UI", 10))
        ok_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; border: none; border-radius: 5px; } QPushButton:hover { background-color: #d32f2f; }")
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def show_success(self, message):
        dialog = QDialog(self)
        dialog.setWindowTitle("Успех")
        dialog.setFixedSize(400, 130)
        dialog.setFont(APP_FONT)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setStyleSheet("QDialog { background-color: white; } QLabel { font-size: 13px; color: #333; }")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 15)
        layout.addWidget(QLabel(message))
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setFixedSize(90, 32)
        ok_btn.setFont(QFont("Segoe UI", 10))
        ok_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; border-radius: 5px; } QPushButton:hover { background-color: #45a049; }")
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def closeEvent(self, event):
        """Перехватываем закрытие окна."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Закрытие программы")
        dialog.setFixedSize(420, 130)
        dialog.setFont(APP_FONT)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setStyleSheet("QDialog { background-color: white; } QLabel { font-size: 13px; color: #333; }")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 15)
        layout.addWidget(QLabel("Вы хотите закрыть программу или свернуть её в трей?"))
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Закрыть программу")
        close_btn.setFixedSize(140, 32)
        close_btn.setFont(QFont("Segoe UI", 10))
        close_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; border: none; border-radius: 5px; } QPushButton:hover { background-color: #d32f2f; }")
        close_btn.clicked.connect(lambda: self.close_app_action(dialog))
        btn_layout.addWidget(close_btn)
        
        tray_btn = QPushButton("Свернуть в трей")
        tray_btn.setFixedSize(140, 32)
        tray_btn.setFont(QFont("Segoe UI", 10))
        tray_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border: none; border-radius: 5px; } QPushButton:hover { background-color: #1976D2; }")
        tray_btn.clicked.connect(lambda: self.close_to_tray_action(dialog))
        btn_layout.addWidget(tray_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedSize(90, 32)
        cancel_btn.setFont(QFont("Segoe UI", 10))
        cancel_btn.setStyleSheet("QPushButton { background-color: #e0e0e0; color: #333; border: none; border-radius: 5px; } QPushButton:hover { background-color: #bdbdbd; }")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        
        dialog.exec_()
        event.ignore()
    
    def close_to_tray_action(self, dialog):
        """Сворачивает программу в трей."""
        dialog.accept()
        self.hide()
        self.close_to_tray.emit()
    
    def close_app_action(self, dialog):
        """Полностью закрывает программу."""
        dialog.accept()
        print("🛑 Пользователь выбрал 'Закрыть программу'")
        self.close_app.emit()