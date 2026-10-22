"""Проверки формул и настоящих сигналов виджетов PyQt5."""

import os
from pathlib import Path
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QSignalSpy, QTest
from PyQt5.QtWidgets import QApplication

from cl2 import Data
from main import MainWindow


APP = QApplication.instance() or QApplication([])


class DataTests(unittest.TestCase):
    def test_initial_values(self):
        self.assertEqual(Data().getData(), (120.0, 500.0, 2.0))

    def test_conversion_from_each_unit(self):
        cases = [
            ("bpm", 60.0, (60.0, 1000.0, 1.0)),
            ("ms", 750.0, (80.0, 750.0, 80.0 / 60.0)),
            ("hz", 3.5, (210.0, 60000.0 / 210.0, 3.5)),
        ]
        for unit, value, expected in cases:
            with self.subTest(unit=unit):
                model = Data()
                signal = QSignalSpy(model.valuesChanged)
                model.set_value(unit, value)
                self.assertEqual(len(signal), 1)
                for actual, target in zip(model.getData(), expected):
                    self.assertAlmostEqual(actual, target)

    def test_range_boundaries(self):
        model = Data()
        for unit, value, bpm in (
            ("bpm", 30.0, 30.0), ("bpm", 300.0, 300.0),
            ("ms", 2000.0, 30.0), ("ms", 200.0, 300.0),
            ("hz", 0.5, 30.0), ("hz", 5.0, 300.0),
        ):
            with self.subTest(unit=unit, value=value):
                model.set_value(unit, value)
                self.assertEqual(model.bpm, bpm)

    def test_invalid_value_does_not_change_model(self):
        model = Data()
        signal = QSignalSpy(model.valuesChanged)
        for unit, value in (
            ("bpm", 0.0), ("ms", -1.0), ("hz", float("nan")),
            ("bpm", float("inf")), ("bpm", 301.0),
            ("ms", 199.0), ("hz", 0.4), ("unknown", 120.0),
        ):
            with self.subTest(unit=unit, value=value):
                with self.assertRaises(ValueError):
                    model.set_value(unit, value)
                self.assertEqual(model.getData(), (120.0, 500.0, 2.0))
        self.assertEqual(len(signal), 0)


class WindowTests(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        APP.processEvents()

    def tearDown(self):
        self.window.close()
        APP.processEvents()

    def assert_fields(self, bpm, milliseconds, hertz):
        self.assertEqual(self.window.bpmSpinBox.value(), round(bpm, 2))
        self.assertEqual(self.window.msSpinBox.value(), round(milliseconds, 2))
        self.assertEqual(self.window.hzSpinBox.value(), round(hertz, 4))

    def test_edit_bpm_updates_other_fields_once(self):
        signal = QSignalSpy(self.window.data.valuesChanged)
        self.window.bpmSpinBox.setValue(90.0)
        self.assert_fields(90.0, 60000.0 / 90.0, 1.5)
        self.assertEqual(len(signal), 1)

    def test_edit_interval_updates_other_fields_once(self):
        signal = QSignalSpy(self.window.data.valuesChanged)
        self.window.msSpinBox.setValue(750.0)
        self.assert_fields(80.0, 750.0, 80.0 / 60.0)
        self.assertEqual(len(signal), 1)

    def test_edit_frequency_keeps_full_model_precision(self):
        signal = QSignalSpy(self.window.data.valuesChanged)
        self.window.hzSpinBox.setValue(2.3333)
        for _ in range(20):
            APP.processEvents()
        self.assert_fields(139.998, 60000.0 / 139.998, 2.3333)
        self.assertAlmostEqual(self.window.data.bpm, 139.998)
        self.assertEqual(len(signal), 1)

    def test_keyboard_input_in_all_three_fields(self):
        for box, text, bpm in (
            (self.window.bpmSpinBox, "90", 90.0),
            (self.window.msSpinBox, "750", 80.0),
            (self.window.hzSpinBox, "1,5", 90.0),
        ):
            with self.subTest(text=text):
                box.setFocus()
                box.selectAll()
                QTest.keyClicks(box, text)
                QTest.keyClick(box, Qt.Key_Return)
                APP.processEvents()
                self.assertAlmostEqual(self.window.data.bpm, bpm)
                self.assert_fields(bpm, 60000.0 / bpm, bpm / 60.0)

    def test_out_of_range_values_are_clamped_by_widgets(self):
        for box, expected_min_bpm, expected_max_bpm in (
            (self.window.bpmSpinBox, 30.0, 300.0),
            (self.window.msSpinBox, 300.0, 30.0),
            (self.window.hzSpinBox, 30.0, 300.0),
        ):
            box.setValue(0.0)
            self.assertEqual(self.window.data.bpm, expected_min_bpm)
            box.setValue(99999.0)
            self.assertEqual(self.window.data.bpm, expected_max_bpm)

    def test_reset_button(self):
        self.window.msSpinBox.setValue(750.0)
        QTest.mouseClick(self.window.resetButton, Qt.LeftButton)
        self.assert_fields(120.0, 500.0, 2.0)

    def test_pulse_timer_follows_tempo_and_stops(self):
        self.window.bpmSpinBox.setValue(300.0)
        signal = QSignalSpy(self.window.beat_timer.timeout)
        QTest.mouseClick(self.window.pulseButton, Qt.LeftButton)
        self.assertTrue(self.window.beat_timer.isActive())
        self.assertEqual(self.window.beat_timer.interval(), 200)
        QTest.qWait(260)
        self.assertGreaterEqual(len(signal), 1)
        self.window.hzSpinBox.setValue(1.0)
        self.assertEqual(self.window.beat_timer.interval(), 1000)
        QTest.mouseClick(self.window.pulseButton, Qt.LeftButton)
        self.assertFalse(self.window.beat_timer.isActive())
        self.assertFalse(self.window.flash_timer.isActive())
        self.assertFalse(self.window.pulseDot.property("active"))

    def test_closing_window_stops_timers(self):
        self.window.pulseButton.setChecked(True)
        self.window.close()
        self.assertFalse(self.window.beat_timer.isActive())
        self.assertFalse(self.window.flash_timer.isActive())


if __name__ == "__main__":
    unittest.main()
