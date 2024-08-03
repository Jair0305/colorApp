import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, \
    QColorDialog, QLineEdit, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDialog
from PyQt5.QtGui import QColor, QPainter, QBrush, QCursor, QScreen
from PyQt5.QtCore import Qt, QTimer, pyqtSignal


class ColorChangerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Color Changer")
        self.setGeometry(100, 100, 400, 400)

        self.color = QColor("#000000")

        self.setupUI()

    def setupUI(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Gráficos para mostrar el círculo
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view)

        self.circle_item = QGraphicsEllipseItem(50, 50, 100, 100)
        self.circle_item.setBrush(QBrush(self.color))
        self.scene.addItem(self.circle_item)

        # Etiqueta y campo de entrada para color hexadecimal
        self.hex_label = QLabel("Hex:")
        self.hex_entry = QLineEdit()
        self.hex_entry.setText(self.color.name())
        self.hex_entry.textChanged.connect(self.update_color_from_hex)

        hex_layout = QHBoxLayout()
        hex_layout.addWidget(self.hex_label)
        hex_layout.addWidget(self.hex_entry)
        self.layout.addLayout(hex_layout)

        # Etiquetas y campos de entrada para componentes RGB
        self.rgb_label = QLabel("RGB:")
        self.r_entry = QLineEdit()
        self.r_entry.setMaxLength(3)

        self.g_entry = QLineEdit()
        self.g_entry.setMaxLength(3)

        self.b_entry = QLineEdit()
        self.b_entry.setMaxLength(3)

        self.r_entry.setText(str(self.color.red()))
        self.g_entry.setText(str(self.color.green()))
        self.b_entry.setText(str(self.color.blue()))

        self.r_entry.textChanged.connect(self.update_color_from_rgb)
        self.g_entry.textChanged.connect(self.update_color_from_rgb)
        self.b_entry.textChanged.connect(self.update_color_from_rgb)

        rgb_layout = QHBoxLayout()
        rgb_layout.addWidget(self.rgb_label)
        rgb_layout.addWidget(self.r_entry)
        rgb_layout.addWidget(self.g_entry)
        rgb_layout.addWidget(self.b_entry)
        self.layout.addLayout(rgb_layout)

        # Conectar el evento de clic para abrir el selector de color
        self.circle_item.mousePressEvent = self.choose_color

        # Botón para abrir la ventana de captura de color
        self.color_capture_button = QPushButton("Capture Color")
        self.color_capture_button.clicked.connect(self.open_color_capture_window)
        self.layout.addWidget(self.color_capture_button)

    def choose_color(self, event):
        color = QColorDialog.getColor(self.color, self, "Choose Color")
        if color.isValid():
            self.color = color
            self.update_circle_color()
            self.update_entries(block_signals=True)

    def update_circle_color(self):
        self.circle_item.setBrush(QBrush(self.color))
        self.scene.update()

    def update_entries(self, block_signals=False):
        if block_signals:
            self.hex_entry.blockSignals(True)
            self.r_entry.blockSignals(True)
            self.g_entry.blockSignals(True)
            self.b_entry.blockSignals(True)

        self.hex_entry.setText(self.color.name())
        self.r_entry.setText(str(self.color.red()))
        self.g_entry.setText(str(self.color.green()))
        self.b_entry.setText(str(self.color.blue()))

        if block_signals:
            self.hex_entry.blockSignals(False)
            self.r_entry.blockSignals(False)
            self.g_entry.blockSignals(False)
            self.b_entry.blockSignals(False)

    def update_color_from_hex(self):
        hex_value = self.hex_entry.text()
        if not hex_value:
            hex_value = "#000000"
        color = QColor(hex_value)
        if color.isValid():
            self.color = color
            self.update_circle_color()
            self.update_entries()

    def update_color_from_rgb(self):
        try:
            r = min(255, max(0, int(self.r_entry.text()))) if self.r_entry.text() else 0
            g = min(255, max(0, int(self.g_entry.text()))) if self.g_entry.text() else 0
            b = min(255, max(0, int(self.b_entry.text()))) if self.b_entry.text() else 0
            color = QColor(r, g, b)
            if color.isValid():
                self.color = color
                self.update_circle_color()
                self.update_entries(block_signals=True)
        except ValueError:
            pass

    def open_color_capture_window(self):
        self.color_capture_window = ColorCaptureWindow()
        self.color_capture_window.colorSelected.connect(self.set_color_from_capture)
        self.color_capture_window.show()

    def set_color_from_capture(self, color):
        self.color = color
        self.update_circle_color()
        self.update_entries(block_signals=True)


class ColorCaptureWindow(QDialog):
    colorSelected = pyqtSignal(QColor)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Color Capture")
        self.setGeometry(100, 100, 300, 200)

        self.layout = QVBoxLayout(self)

        self.mouse_pos_label = QLabel("Mouse Position: (0, 0)")
        self.color_label = QLabel("Color: #000000")
        self.rgb_label = QLabel("RGB: (0, 0, 0)")
        self.color_display = QLabel()
        self.color_display.setFixedSize(50, 50)

        self.layout.addWidget(self.mouse_pos_label)
        self.layout.addWidget(self.color_label)
        self.layout.addWidget(self.rgb_label)
        self.layout.addWidget(self.color_display)

        # Timer to update the color under the cursor
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_color_under_cursor)
        self.timer.start(100)

    def update_color_under_cursor(self):
        pos = QCursor.pos()
        self.mouse_pos_label.setText(f"Mouse Position: ({pos.x()}, {pos.y()})")

        screen = QApplication.instance().primaryScreen()
        pixmap = screen.grabWindow(0, pos.x(), pos.y(), 1, 1)
        image = pixmap.toImage()
        color = image.pixelColor(0, 0)

        hex_color = color.name()
        rgb_color = (color.red(), color.green(), color.blue())

        self.color_label.setText(f"Color: {hex_color}")
        self.rgb_label.setText(f"RGB: {rgb_color}")
        self.color_display.setStyleSheet(f"background-color: {hex_color}")

        self.current_color = color

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.colorSelected.emit(self.current_color)
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorChangerApp()
    window.show()
    sys.exit(app.exec_())
