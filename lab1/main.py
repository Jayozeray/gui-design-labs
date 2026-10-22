
import sys
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QMainWindow,
    QMessageBox,
)

BASE_DIR = Path(__file__).resolve().parent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загружаем форму .ui
        uic.loadUi(str(BASE_DIR / "main.ui"), self)
        self.setFixedSize(self.size())

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(120, 88, 145, 35))
        self.contentLabel.setGraphicsEffect(shadow)

        self.showing_image = False
        self.original_text = self.contentLabel.text()
        self.picture = QPixmap(str(BASE_DIR / "assets" / "cat.png"))

        # Сигнал clicked кнопки вызывает слот toggle_content
        self.toggleButton.clicked.connect(self.toggle_content)

    @pyqtSlot()
    def toggle_content(self):
        """Каждое нажатие меняет содержимое одного и того же QLabel."""
        if self.showing_image:
            self.contentLabel.clear()
            self.contentLabel.setText(self.original_text)
            self.toggleButton.setText("Показать картинку")
            self.showing_image = False
        else:
            if self.picture.isNull():
                QMessageBox.warning(
                    self,
                    "Картинка не найдена",
                    "Проверьте, что файл assets/cat.png находится в папке проекта.",
                )
                return

            # Уменьшаем изображение, сохраняя его пропорции
            image_size = self.contentLabel.contentsRect().size()
            image_size.setWidth(max(1, image_size.width() - 32))
            image_size.setHeight(max(1, image_size.height() - 32))
            scaled_picture = self.picture.scaled(
                image_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            self.contentLabel.clear()
            self.contentLabel.setPixmap(scaled_picture)
            self.toggleButton.setText("Показать текст")
            self.showing_image = True


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(BASE_DIR / "assets" / "icon.png")))

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
