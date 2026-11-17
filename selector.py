from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QCursor, QFont


class SelectorWindow(QWidget):
    """Окно выделения области экрана с затемнением."""
    
    screenshot_taken = pyqtSignal(int, int, int, int)
    selection_cancelled = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Переменные для выделения (глобальные координаты экрана)
        self.start_global = None
        self.current_global = None
        self.is_selecting = False
        self.min_size = 10
    
    def init_ui(self):
        """Инициализация окна."""
        # Получаем геометрию виртуального десктопа
        virtual_geometry = QRect()
        for screen in QApplication.screens():
            virtual_geometry = virtual_geometry.united(screen.geometry())
        
        print(f"📐 Геометрия окна выделения: x={virtual_geometry.x()}, y={virtual_geometry.y()}, "
              f"ширина={virtual_geometry.width()}, высота={virtual_geometry.height()}")
        
        # Устанавливаем геометрию
        self.setGeometry(virtual_geometry)
        
        # Поверх всех окон, без рамки
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint
        )
        
        # Полупрозрачный фон
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Курсор — перекрестие
        self.setCursor(QCursor(Qt.CrossCursor))
        self.setMouseTracking(True)
        
        self.hide()
    
    def paintEvent(self, event):
        """Рисуем затемнение и рамку выделения."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Затемнение всего экрана
        painter.fillRect(self.rect(), QColor(0, 0, 0, 128))
        
        if self.start_global and self.current_global:
            # Конвертируем глобальные координаты в локальные координаты окна
            window_pos = self.pos()  # Позиция окна на экране
            
            start_local = self.start_global - window_pos
            current_local = self.current_global - window_pos
            
            # Вычисляем прямоугольник в локальных координатах
            x = min(start_local.x(), current_local.x())
            y = min(start_local.y(), current_local.y())
            width = abs(current_local.x() - start_local.x())
            height = abs(current_local.y() - start_local.y())
            
            rect = QRect(x, y, width, height)
            
            # Вырезаем яркую область
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
            # Рисуем рамку
            pen = QPen(QColor("#4CAF50"), 2)
            painter.setPen(pen)
            painter.drawRect(rect)
            
            # Показываем размеры
            if width > 30 and height > 30:
                size_text = f"{width} × {height}"
                painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
                painter.setPen(QColor("#FFFFFF"))
                
                text_x = x + 5
                text_y = y + 20
                
                text_rect = QRect(text_x, text_y - 18, 80, 22)
                painter.fillRect(text_rect, QColor(0, 0, 0, 180))
                painter.drawText(text_rect, Qt.AlignCenter, size_text)
        
        painter.end()
    
    def mousePressEvent(self, event):
        """Начало выделения."""
        if event.button() == Qt.LeftButton:
            # Сохраняем глобальные координаты
            self.start_global = event.globalPos()
            self.current_global = event.globalPos()
            self.is_selecting = True
            self.update()
    
    def mouseMoveEvent(self, event):
        """Обновление выделения."""
        if self.is_selecting:
            self.current_global = event.globalPos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Конец выделения."""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            
            # Используем глобальные координаты для сигнала
            x = min(self.start_global.x(), self.current_global.x())
            y = min(self.start_global.y(), self.current_global.y())
            width = abs(self.current_global.x() - self.start_global.x())
            height = abs(self.current_global.y() - self.start_global.y())
            
            if width >= self.min_size and height >= self.min_size:
                self.screenshot_taken.emit(x, y, width, height)
            
            self.start_global = None
            self.current_global = None
            self.update()
    
    def keyPressEvent(self, event):
        """Обработка клавиш."""
        if event.key() == Qt.Key_Escape:
            self.selection_cancelled.emit()
            self.close()
    
    def show_selector(self):
        """Показывает окно выделения."""
        self.show()
        QApplication.processEvents()  # Принудительно отрисовываем окно
        self.activateWindow()
        self.raise_()