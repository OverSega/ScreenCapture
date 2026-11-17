import mss
import mss.tools
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import sys


def get_all_monitors_info():
    """Получает информацию о всех мониторах."""
    with mss.mss() as sct:
        monitors = sct.monitors
        return monitors


def capture_region(x, y, width, height):
    """
    Делает скриншот указанной области экрана.
    Поддерживает несколько мониторов (отрицательные координаты).
    Возвращает QImage или None при ошибке.
    """
    try:
        with mss.mss() as sct:
            # Получаем информацию о всех мониторах
            monitors = sct.monitors
            
            # Находим монитор, который содержит нужную область
            # monitors[0] — это "весь экран" (все мониторы вместе)
            # monitors[1], monitors[2], ... — отдельные мониторы
            
            # Для простоты используем весь экран (monitors[0])
            # и вырезаем нужную область
            full_screen = monitors[0]
            
            # Координаты области относительно всего экрана
            # mss использует "left", "top", "width", "height"
            region = {
                "left": x,
                "top": y,
                "width": width,
                "height": height
            }
            
            # Делаем скриншот
            screenshot = sct.grab(region)
            
            # Конвертируем в QImage
            # mss возвращает данные в формате BGRA (Windows)
            # QImage ожидает Format_ARGB32
            image = QImage(
                screenshot.rgb,  # Конвертируем в RGB
                screenshot.width,
                screenshot.height,
                screenshot.width * 3,  # Bytes per line (3 канала RGB)
                QImage.Format_RGB888
            )
            
            # Копируем изображение (чтобы данные не потерялись при закрытии mss)
            image = image.copy()
            
            return image
            
    except Exception as e:
        print(f"❌ Ошибка захвата экрана: {e}", file=sys.stderr)
        return None


def copy_image_to_clipboard(image):
    """
    Помещает QImage в буфер обмена.
    Возвращает True при успехе, False при ошибке.
    """
    try:
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(QPixmap.fromImage(image))
        print("✅ Изображение скопировано в буфер обмена")
        return True
    except Exception as e:
        print(f"❌ Ошибка копирования в буфер: {e}", file=sys.stderr)
        return False


def clear_clipboard():
    """Очищает буфер обмена."""
    try:
        clipboard = QApplication.clipboard()
        clipboard.clear()
        print("🗑 Буфер обмена очищен")
        return True
    except Exception as e:
        print(f"❌ Ошибка очистки буфера: {e}", file=sys.stderr)
        return False


def check_clipboard_has_image():
    """Проверяет, есть ли изображение в буфере обмена."""
    try:
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()
        return not pixmap.isNull()
    except Exception as e:
        print(f"❌ Ошибка проверки буфера: {e}", file=sys.stderr)
        return False
def capture_fullscreen():
    """
    Делает скриншот всего экрана (всех мониторов).
    Возвращает QImage или None при ошибке.
    """
    try:
        with mss.mss() as sct:
            # monitors[0] — это весь виртуальный десктоп
            full_screen = sct.monitors[0]
            
            # Делаем скриншот
            screenshot = sct.grab(full_screen)
            
            # Конвертируем в QImage
            image = QImage(
                screenshot.rgb,
                screenshot.width,
                screenshot.height,
                screenshot.width * 3,
                QImage.Format_RGB888
            )
            
            # Копируем изображение
            image = image.copy()
            
            return image
            
    except Exception as e:
        print(f"❌ Ошибка захвата полного экрана: {e}", file=sys.stderr)
        return None    