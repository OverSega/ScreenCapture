import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QRect, QSharedMemory
from settings_window import SettingsWindow, APP_FONT
from tray import TrayIcon
from selector import SelectorWindow
from hotkeys import HotkeyManager
import capture
import pyautogui
import config

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

try:
    import pygetwindow as gw
    HAS_GETWINDOW = True
except ImportError:
    HAS_GETWINDOW = False

try:
    import win32api
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("⚠️ pywin32 не установлен. Отправка может не работать.")


class App:
    """Главный класс приложения."""
    
    def __init__(self):
        # Проверка единственного экземпляра
        self.shared_memory = QSharedMemory("ScreenCapture_SingleInstance")
        if not self.shared_memory.create(1):
            QMessageBox.warning(
                None,
                "ScreenCapture",
                "Программа уже запущена!\n\nПроверьте системный трей (возле часов)."
            )
            sys.exit(1)
        
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setFont(APP_FONT)
        
        # Обработчик выхода
        self.app.aboutToQuit.connect(self.on_about_to_quit)
        
        self.flash_window = None
        self.selector_active = False
        self._clear_timer = None
        
        try:
            pixmap = QPixmap("icon.png")
            pixmap = pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.app.setWindowIcon(QIcon(pixmap))
        except Exception as e:
            print(f"Ошибка установки иконки приложения: {e}")
        
        self.settings_window = SettingsWindow()
        self.tray_icon = TrayIcon(self.settings_window)
        
        self.selector = SelectorWindow()
        self.selector.screenshot_taken.connect(self.on_screenshot_taken)
        self.selector.selection_cancelled.connect(self.on_selection_cancelled)
        
        self.hotkey_manager = HotkeyManager(self)
        
        self.settings_window.start_assigning.connect(lambda: self.hotkey_manager.set_assigning_mode(True))
        self.settings_window.stop_assigning.connect(lambda: self.hotkey_manager.set_assigning_mode(False))
        self.settings_window.settings_saved.connect(self.hotkey_manager.reload_hotkeys)
        self.settings_window.close_app.connect(self.exit_application)
        
        print("⏳ Предварительная инициализация...")
        
        self.selector.show()
        self.app.processEvents()
        self.selector.hide()
        
        test_image = capture.capture_region(0, 0, 100, 100)
        if test_image:
            print("✅ mss инициализирован")
        
        try:
            test_pixmap = QPixmap(10, 10)
            test_pixmap.fill(Qt.white)
            self.app.clipboard().setPixmap(test_pixmap)
            print("✅ Буфер обмена инициализирован")
        except Exception as e:
            print(f"⚠️ Не удалось инициализировать буфер: {e}")
        
        try:
            test_widget = QWidget()
            test_widget.resize(100, 100)
            test_widget.setAttribute(Qt.WA_TranslucentBackground)
            test_widget.show()
            self.app.processEvents()
            
            from PyQt5.QtGui import QPainter
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(0, 0, 50, 50, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.end()
            
            test_widget.hide()
            test_widget.deleteLater()
            print("✅ Графический контекст инициализирован")
        except Exception as e:
            print(f"⚠️ Не удалось инициализировать графический контекст: {e}")
        
        print("✅ Предварительная инициализация завершена\n")
        
        self.hotkey_manager.start()
        self.settings_window.show()
    
    def on_about_to_quit(self):
        """Вызывается перед завершением приложения."""
        print("🛑 Завершение приложения...")
        self.hotkey_manager.stop()
        if self.tray_icon:
            self.tray_icon.hide()
        # Освобождаем shared memory для возможности повторного запуска
        if self.shared_memory.isAttached():
            self.shared_memory.detach()
        print("✅ Приложение завершено")
    
    def exit_application(self):
        """Полностью закрывает приложение."""
        print("🛑 Полный выход из приложения")
        self.hotkey_manager.stop()
        if self.tray_icon:
            self.tray_icon.hide()
        QApplication.quit()
    
    def on_screenshot_key(self):
        """Клавиша выделения области."""
        print(f"📸 [DEBUG] on_screenshot_key вызван. selector_active={self.selector_active}")
        
        if self.selector_active:
            print("⚠️ Окно выделения уже активно, игнорируем")
            return
        
        self.selector_active = True
        print("📸 Открываем окно выделения")
        
        try:
            self.selector.show_selector()
        except Exception as e:
            print(f"❌ Ошибка открытия окна выделения: {e}")
            self.selector_active = False
    
    def on_fullscreen_key(self):
        """Клавиша полного экрана."""
        self._cancel_clear()
        
        print("📸 Скриншот всего экрана...")
        image = capture.capture_fullscreen()
        
        if image:
            success = capture.copy_image_to_clipboard(image)
            if success:
                print("✅ Скриншот полного экрана скопирован в буфер")
                self.show_flash()
            else:
                print("❌ Не удалось скопировать в буфер")
        else:
            print("❌ Не удалось сделать скриншот")
    
    def on_send_key(self):
        """Клавиша отправки."""
        print("📤 [SEND] Нажата клавиша отправки")
        
        if HAS_GETWINDOW:
            try:
                active = gw.getActiveWindow()
                print(f"📤 [SEND] Активное окно: {active.title if active else 'None'}")
            except Exception as e:
                print(f"📤 [SEND] Не удалось получить активное окно: {e}")
        
        has_image = capture.check_clipboard_has_image()
        print(f"📤 [SEND] Буфер содержит изображение: {has_image}")
        
        if not has_image:
            print("⚠️ [SEND] Буфер пуст — сначала сделайте скриншот")
            return
        
        print("📤 [SEND] Отправляем Ctrl+V...")
        
        if HAS_WIN32:
            try:
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(ord('V'), 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                print("✅ [SEND] Ctrl+V отправлен через win32api")
            except Exception as e:
                print(f"❌ [SEND] Ошибка win32api Ctrl+V: {e}")
                try:
                    pyautogui.hotkey('ctrl', 'v')
                except Exception as e2:
                    print(f"❌ [SEND] Ошибка pyautogui Ctrl+V: {e2}")
                    return
        else:
            try:
                pyautogui.hotkey('ctrl', 'v')
            except Exception as e:
                print(f"❌ [SEND] Ошибка Ctrl+V: {e}")
                return
        
        QTimer.singleShot(1000, self._press_enter)
    
    def _press_enter(self):
        print("📤 [SEND] Отправляем Enter...")
        
        if HAS_WIN32:
            try:
                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                print("✅ [SEND] Enter нажат через win32api")
            except Exception as e:
                print(f"❌ [SEND] Ошибка win32api Enter: {e}")
                try:
                    pyautogui.press('enter')
                except Exception as e2:
                    print(f"❌ [SEND] Ошибка pyautogui Enter: {e2}")
                    return
        else:
            try:
                pyautogui.press('enter')
            except Exception as e:
                print(f"❌ [SEND] Ошибка Enter: {e}")
                return
        
        self._schedule_clear()
    
    def _schedule_clear(self):
        """Планирует отменяемую очистку буфера через 2 секунды."""
        cfg = config.load_config()
        if not cfg.get("clear_after_send", True):
            return
        self._cancel_clear()
        self._clear_timer = QTimer()
        self._clear_timer.setSingleShot(True)
        self._clear_timer.timeout.connect(self._clear_clipboard)
        self._clear_timer.start(2000)
    
    def _cancel_clear(self):
        """Отменяет отложенную очистку буфера."""
        if self._clear_timer and self._clear_timer.isActive():
            self._clear_timer.stop()
            self._clear_timer = None
            print("⏹ [SEND] Отменена отложенная очистка буфера (сделан новый скрин)")
    
    def _clear_clipboard(self):
        """Очищает буфер обмена."""
        print("🗑 [SEND] Очищаем буфер обмена...")
        capture.clear_clipboard()
        self._clear_timer = None
    
    def on_screenshot_taken(self, x, y, width, height):
        print(f"📸 Выделена область: x={x}, y={y}, ширина={width}, высота={height}")
        
        self._cancel_clear()
        
        self.selector_active = False
        self.selector.hide()
        
        image = capture.capture_region(x, y, width, height)
        
        if image:
            success = capture.copy_image_to_clipboard(image)
            if success:
                print(f"✅ Скриншот ({width}×{height}) скопирован в буфер")
                self.show_flash()
            else:
                print("❌ Не удалось скопировать в буфер")
        else:
            print("❌ Не удалось сделать скриншот")
    
    def show_flash(self):
        try:
            if self.flash_window:
                self.flash_window.close()
                self.flash_window = None
            
            self.flash_window = QWidget()
            self.flash_window.setWindowFlags(
                Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
            )
            self.flash_window.setAttribute(Qt.WA_TranslucentBackground)
            
            virtual_geometry = QRect()
            for screen in QApplication.screens():
                virtual_geometry = virtual_geometry.united(screen.geometry())
            self.flash_window.setGeometry(virtual_geometry)
            
            self.flash_window.setStyleSheet("background-color: rgba(255, 255, 255, 200);")
            self.flash_window.show()
            
            QTimer.singleShot(100, self._close_flash)
        except Exception as e:
            print(f"⚠️ Ошибка вспышки: {e}")
    
    def _close_flash(self):
        if self.flash_window:
            self.flash_window.close()
            self.flash_window.deleteLater()
            self.flash_window = None
    
    def on_selection_cancelled(self):
        print("❌ Выделение отменено (Esc)")
        self.selector_active = False
        self.selector.hide()
    
    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = App()
    app.run()