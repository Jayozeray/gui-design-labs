"""Лабораторная работа №2. «Пульс»: сигналы и слоты PyQt5."""

import sys
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import QLocale, QTimer, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow

from cl1 import ValueField
from cl2 import Data


BASE_DIR = Path(__file__).resolve().parent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(BASE_DIR / "main.ui"), self)
        self.setStyleSheet((BASE_DIR / "styles.qss").read_text(encoding="utf-8"))

        # Русская запись дробных чисел: десятичная запятая.
        for spinbox in (self.bpmSpinBox, self.msSpinBox, self.hzSpinBox):
            spinbox.setLocale(QLocale(QLocale.Russian, QLocale.Russia))

        self.data = Data(self)
        self.bpm_field = ValueField(self.bpmSpinBox, "bpm", self)
        self.ms_field = ValueField(self.msSpinBox, "ms", self)
        self.hz_field = ValueField(self.hzSpinBox, "hz", self)

        # Поле посылает собственный сигнал в слот объекта Data
        for field in (self.bpm_field, self.ms_field, self.hz_field):
            field.valueEdited.connect(self.data.set_value)

        # Модель посылает результат в слот главного окна
        self.data.valuesChanged.connect(self.sync_fields)
        self.resetButton.clicked.connect(self.data.reset)

        # Два таймера: один задаёт ритм, второй гасит короткую вспышку
        self.beat_timer = QTimer(self)
        self.beat_timer.timeout.connect(self.flash_beat)
        self.flash_timer = QTimer(self)
        self.flash_timer.setSingleShot(True)
        self.flash_timer.setInterval(90)
        self.flash_timer.timeout.connect(self.dim_beat)
        self.pulseButton.toggled.connect(self.set_running)

        self.sync_fields(*self.data.getData())
        self.dim_beat()

    @pyqtSlot(float, float, float)
    def sync_fields(self, bpm, milliseconds, hertz):
        """Получаем результат модели и обновляем все поля."""
        self.bpm_field.set_value(bpm)
        self.ms_field.set_value(milliseconds)
        self.hz_field.set_value(hertz)

        self.summaryLabel.setText(
            f"<b>{self.format_number(bpm)}</b> BPM"
            f" &nbsp; = &nbsp; <b>{self.format_number(milliseconds)}</b> мс между ударами"
            f" &nbsp; = &nbsp; <b>{self.format_number(hertz, 4)}</b> удара/с"
        )
        if self.beat_timer.isActive():
            self.beat_timer.setInterval(round(milliseconds))

    @staticmethod
    def format_number(value, decimals=2):
        return f"{value:.{decimals}f}".rstrip("0").rstrip(".").replace(".", ",")

    @pyqtSlot(bool)
    def set_running(self, running):
        if running:
            self.flash_beat()
            self.beat_timer.start(round(self.data.getData()[1]))
            self.pulseButton.setText("Остановить ритм")
            self.pulseStatusLabel.setText("Индикатор мигает в темп трека")
        else:
            self.beat_timer.stop()
            self.flash_timer.stop()
            self.dim_beat()
            self.pulseButton.setText("Показать ритм")
            self.pulseStatusLabel.setText("Включи индикатор, чтобы увидеть ритм")

    @pyqtSlot()
    def flash_beat(self):
        self.set_dot_active(True)
        self.flash_timer.start()

    @pyqtSlot()
    def dim_beat(self):
        self.set_dot_active(False)

    def set_dot_active(self, active):
        self.pulseDot.setProperty("active", active)
        self.pulseDot.style().unpolish(self.pulseDot)
        self.pulseDot.style().polish(self.pulseDot)
        self.pulseDot.update()

    def closeEvent(self, event):
        self.beat_timer.stop()
        self.flash_timer.stop()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(BASE_DIR / "assets" / "icon.svg")))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
