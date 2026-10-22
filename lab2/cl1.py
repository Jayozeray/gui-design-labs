"""Поле ввода, которое передаёт изменения собственным сигналом."""

from PyQt5.QtCore import QObject, QSignalBlocker, pyqtSignal, pyqtSlot


class ValueField(QObject):
    # Сигнал передаёт название единицы измерения и новое значение.
    valueEdited = pyqtSignal(str, float)

    def __init__(self, spinbox, unit, parent=None):
        super().__init__(parent)
        self.spinbox = spinbox
        self.unit = unit
        self.spinbox.valueChanged[float].connect(self.on_value_changed)

    @pyqtSlot(float)
    def on_value_changed(self, value):
        """Передаём значение модели, когда пользователь меняет поле."""
        self.valueEdited.emit(self.unit, value)

    @pyqtSlot(float)
    def set_value(self, value):
        """Обновляем поле из модели без запуска нового пересчёта."""
        # Не трогаем текст и курсор, если отображаемое число уже совпадает.
        if self.spinbox.value() == round(value, self.spinbox.decimals()):
            return

        # Без блокировки setValue() снова вызовет valueChanged,
        # что приведёт к лишним пересчётам и накоплению округлений.
        with QSignalBlocker(self.spinbox):
            self.spinbox.setValue(value)
