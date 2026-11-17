from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import os


class TrayIcon(QSystemTrayIcon):
    """Системный трей приложения."""
    
    def __init__(self, settings_window, parent=None):
        super().__init__(parent)
        self.settings_window = settings_window
        
        # Загружаем иконку (ищем в текущей директории)
        icon = self._load_icon()
        self.setIcon(icon)
        
        # Тултип
        self.setToolTip("ScreenCapture — готов к работе")
        
        # Создаём меню
        self._create_menu()
        
        # Двойной клик — открыть настройки
        self.activated.connect(self.on_tray_activated)
        
        # Показываем иконку
        self.show()
        
        print("✅ Иконка в трее создана")
    
    def _load_icon(self):
        """Загружает иконку из PNG файла."""
        # Ищем иконку в текущей директории
        icon_path = os.path.join(os.getcwd(), "icon.png")
        
        if not os.path.exists(icon_path):
            print(f"⚠️ Иконка не найдена: {icon_path}")
            # Создаём простую иконку программно
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.blue)
            return QIcon(pixmap)
        
        try:
            pixmap = QPixmap(icon_path)
            if pixmap.isNull():
                print("⚠️ Не удалось загрузить иконку")
                pixmap = QPixmap(32, 32)
                pixmap.fill(Qt.blue)
            else:
                pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            return QIcon(pixmap)
        except Exception as e:
            print(f"❌ Ошибка загрузки иконки: {e}")
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.blue)
            return QIcon(pixmap)
    
    def _create_menu(self):
        """Создаёт контекстное меню трея."""
        menu = QMenu()
        
        # Настройки
        settings_action = QAction("⚙ Настройки", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        # Показать/Скрыть
        self.toggle_action = QAction("👁 Скрыть окно", self)
        self.toggle_action.triggered.connect(self.toggle_window)
        menu.addAction(self.toggle_action)
        
        menu.addSeparator()
        
        # Выход
        exit_action = QAction("❌ Выход", self)
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)
        
        self.setContextMenu(menu)
    
    def on_tray_activated(self, reason):
        """Обработка активации иконки трея."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_settings()
    
    def show_settings(self):
        """Показывает окно настроек."""
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
        self.toggle_action.setText("👁 Скрыть окно")
    
    def toggle_window(self):
        """Переключает видимость окна настроек."""
        if self.settings_window.isVisible():
            self.settings_window.hide()
            self.toggle_action.setText("👁 Показать окно")
        else:
            self.settings_window.show()
            self.settings_window.raise_()
            self.settings_window.activateWindow()
            self.toggle_action.setText("👁 Скрыть окно")
    
    def exit_app(self):
        """Закрывает приложение."""
        print("🛑 Выход из приложения через трей")
        QApplication.quit()
    
    def show_notification(self, title, message, duration=3000):
        """Показывает уведомление."""
        self.showMessage(title, message, QSystemTrayIcon.Information, duration)