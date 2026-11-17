import keyboard
import config
import time
import threading
from PyQt5.QtCore import QObject, pyqtSignal


class HotkeySignals(QObject):
    """QObject-мост для безопасного вызова методов из фонового потока."""
    screenshot_requested = pyqtSignal()
    send_requested = pyqtSignal()
    fullscreen_requested = pyqtSignal()


class HotkeyManager:
    """Менеджер глобальных горячих клавиш на библиотеке keyboard."""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.is_assigning_key = False
        self._lock = threading.Lock()
        
        # Зарегистрированные hotkey-идентификаторы
        self._registered_hotkeys = []
        
        # Cooldown
        self._last_action_time = 0
        self._cooldown = 0.5
        
        # Мост сигналов (создаётся в главном потоке)
        self.signals = HotkeySignals()
        self.signals.screenshot_requested.connect(self.app.on_screenshot_key)
        self.signals.send_requested.connect(self.app.on_send_key)
        self.signals.fullscreen_requested.connect(self.app.on_fullscreen_key)
    
    def start(self):
        """Запускает слушатель горячих клавиш."""
        try:
            self._refresh_hotkeys()
            print("✅ Слушатель горячих клавиш запущен (keyboard)")
        except Exception as e:
            print(f"❌ Ошибка запуска слушателя: {e}")
            import traceback
            traceback.print_exc()
    
    def stop(self):
        """Останавливает все горячие клавиши."""
        try:
            for hk_id in self._registered_hotkeys:
                try:
                    keyboard.remove_hotkey(hk_id)
                except Exception:
                    pass
            self._registered_hotkeys.clear()
            print("🛑 Слушатель горячих клавиш остановлен")
        except Exception as e:
            print(f"❌ Ошибка остановки: {e}")
    
    def reload_hotkeys(self):
        """Перезагружает горячие клавиши из свежего конфига (после Сохранить)."""
        if self.is_assigning_key:
            # В режиме назначения — не трогаем, после назначения обновится сам
            return
        try:
            self._refresh_hotkeys()
            print("🔄 Горячие клавиши перезагружены из конфига")
        except Exception as e:
            print(f"❌ Ошибка перезагрузки: {e}")
    
    def set_assigning_mode(self, is_assigning):
        """Включает/отключает режим назначения клавиш."""
        with self._lock:
            self.is_assigning_key = is_assigning
        
        if is_assigning:
            self.stop()
            print("⏸️ Горячие клавиши отключены (режим назначения)")
        else:
            self.start()
            print("▶️ Горячие клавиши включены")
    
    def _refresh_hotkeys(self):
        """Перерегистрирует горячие клавиши из конфига (читает файл напрямую)."""
        # Удаляем старые
        for hk_id in self._registered_hotkeys:
            try:
                keyboard.remove_hotkey(hk_id)
            except Exception:
                pass
        self._registered_hotkeys.clear()
        
        cfg = config.load_config()
        
        screenshot_key = config.get_hotkey(cfg, "screenshot")
        send_key = config.get_hotkey(cfg, "send")
        fullscreen_key = config.get_hotkey(cfg, "fullscreen")
        
        if screenshot_key:
            try:
                hk_id = keyboard.add_hotkey(
                    screenshot_key.lower(),
                    self._on_screenshot,
                    suppress=True
                )
                self._registered_hotkeys.append(hk_id)
                print(f"   📌 Скриншот: {screenshot_key}")
            except Exception as e:
                print(f"   ⚠️ Не удалось зарегистрировать {screenshot_key}: {e}")
        
        if send_key:
            try:
                hk_id = keyboard.add_hotkey(
                    send_key.lower(),
                    self._on_send,
                    suppress=True
                )
                self._registered_hotkeys.append(hk_id)
                print(f"   📌 Отправка: {send_key}")
            except Exception as e:
                print(f"   ⚠️ Не удалось зарегистрировать {send_key}: {e}")
        
        if fullscreen_key:
            try:
                hk_id = keyboard.add_hotkey(
                    fullscreen_key.lower(),
                    self._on_fullscreen,
                    suppress=True
                )
                self._registered_hotkeys.append(hk_id)
                print(f"   📌 Полный экран: {fullscreen_key}")
            except Exception as e:
                print(f"   ⚠️ Не удалось зарегистрировать {fullscreen_key}: {e}")
    
    def _check_cooldown(self):
        """Проверяет cooldown. Возвращает True, если действие разрешено."""
        current_time = time.monotonic()
        with self._lock:
            if current_time - self._last_action_time < self._cooldown:
                return False
            self._last_action_time = current_time
            return True
    
    def _on_screenshot(self):
        if not self._check_cooldown():
            return
        print(f"⌨️ [HOTKEY] Скриншот")
        self.signals.screenshot_requested.emit()
    
    def _on_send(self):
        if not self._check_cooldown():
            return
        print(f"⌨️ [HOTKEY] Отправка")
        self.signals.send_requested.emit()
    
    def _on_fullscreen(self):
        if not self._check_cooldown():
            return
        print(f"⌨️ [HOTKEY] Полный экран")
        self.signals.fullscreen_requested.emit()