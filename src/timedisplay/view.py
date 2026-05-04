import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QColor,
    QContextMenuEvent,
    QFont,
    QFontMetrics,
    QMouseEvent,
    QPainter,
)
from PySide6.QtWidgets import QApplication, QColorDialog, QLabel, QMenu, QVBoxLayout, QWidget


class TimeDisplay(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self._dragging = False
        self.oldPosition = None

        self.color = None

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint)
        self.setup_widgets()
        self.setup_qss()

    def setup_widgets(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.time_label = QLabel("--:--:--", self)
        font = QFont()
        font.setPointSize(24)
        self.time_label.setFont(font)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.time_label)

    def update_clock(self) -> None:
        if not self.time_label:
            return
        self.time_label.setText(datetime.datetime.now().strftime("%H:%M:%S"))

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self)

        exit_action = QAction("exit", self)
        exit_action.triggered.connect(QApplication.quit)

        color_action = QAction("change color", self)
        color_action.triggered.connect(self.get_color)

        menu.addAction(exit_action)
        menu.addAction(color_action)
        menu.exec_(event.globalPos())

    def setup_qss(self) -> None:
        """QSSを設定

        font_color: 文字の色 rgb
        font_size: フォントのサイズ
        """
        self.time_label.setStyleSheet("""
            QLabel {
                color: rgb(0, 0, 0);
                font-weight: bold;
                background: transparent;
            }
        """)

    def update_qss(self):
        if self.color is not None:
            self.time_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.color.name()};
                    font-weight: bold;
                }}
            """)

    def get_color(self):
        self.color = QColorDialog.getColor(parent=self)
        print(self.color.name())

        self.update_qss()

    def update_font_size(self):
        text = self.time_label.text()
        font = QFont()
        font.setBold(True)

        low, high = 1, 300

        while low <= high:
            mid = (low + high) // 2
            font.setPixelSize(mid)
            metrics = QFontMetrics(font)
            rect = metrics.boundingRect(text)

            if (
                rect.width() <= self.time_label.width()
                and rect.height() <= self.time_label.height()
            ):
                low = mid + 1
            else:
                high = mid - 1

        font.setPixelSize(high)
        self.time_label.setFont(font)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.timer.stop()
        super().closeEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:

        if event.button() == Qt.MouseButton.LeftButton:
            p = event.position()
            is_top, is_bottom, is_left, is_right = (
                p.y() < 5,
                p.y() > self.height() - 5,
                p.x() < 5,
                p.x() > self.width() - 5,
            )
            edges_list = []
            if is_top:
                edges_list.append(Qt.Edge.TopEdge)
            if is_bottom:
                edges_list.append(Qt.Edge.BottomEdge)
            if is_right:
                edges_list.append(Qt.Edge.RightEdge)
            if is_left:
                edges_list.append(Qt.Edge.LeftEdge)
            if edges_list:
                edges = edges_list[0]
                for edge in edges_list[1:]:
                    edges |= edge
                self.windowHandle().startSystemResize(edges)
                return

            self._dragging = True
            self.oldPosition = event.globalPosition()

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        p = event.position()
        margin = 5

        is_top = p.y() < margin
        is_bottom = p.y() > self.height() - margin
        is_left = p.x() < margin
        is_right = p.x() > self.width() - margin

        if self._dragging:
            if self._dragging and self.oldPosition is not None:
                delta = event.globalPosition() - self.oldPosition
                self.move(int(self.x() + delta.x()), int(self.y() + delta.y()))
                self.oldPosition = event.globalPosition()
            return

        # カーソル制御（ホバー時のみ）
        if (is_top and is_left) or (is_bottom and is_right):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif (is_top and is_right) or (is_bottom and is_left):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif is_top or is_bottom:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif is_left or is_right:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(0, 0, 0, 1))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_font_size()
