"""Данные и пересчёт музыкального темпа между тремя величинами."""

import math

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class Data(QObject):
    MIN_BPM = 30.0
    MAX_BPM = 300.0
    DEFAULT_BPM = 120.0

    # После пересчёта отправляем сразу три согласованных значения.
    valuesChanged = pyqtSignal(float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bpm = self.DEFAULT_BPM

    def getData(self):
        """Возвращаем: BPM, миллисекунды между ударами, удары в секунду."""
        return self.bpm, 60000.0 / self.bpm, self.bpm / 60.0

    @pyqtSlot(str, float)
    def set_value(self, unit, value):
        """Принимаем изменение любого поля и пересчитываем остальные."""
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Значение должно быть положительным числом.")

        if unit == "bpm":
            bpm = value
        elif unit == "ms":
            bpm = 60000.0 / value
        elif unit == "hz":
            bpm = value * 60.0
        else:
            raise ValueError("Неизвестная единица измерения: " + unit)

        if not self.MIN_BPM <= bpm <= self.MAX_BPM:
            raise ValueError("Темп должен быть от 30 до 300 BPM.")

        # Храним число без округления, округляются только поля на экране.
        self.bpm = bpm
        self.valuesChanged.emit(*self.getData())

    @pyqtSlot()
    def reset(self):
        self.set_value("bpm", self.DEFAULT_BPM)
