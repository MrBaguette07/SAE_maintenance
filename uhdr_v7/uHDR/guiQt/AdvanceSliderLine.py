# uHDR: HDR image editing software
#   Copyright (C) 2022  remi cozot 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
# hdrCore project 2020-2022
# author: remi.cozot@univ-littoral.fr

# import
# ------------------------------------------------------------------------------------------
# AdvanceSliderLine.py
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel, QLineEdit, QSlider
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt, pyqtSignal, QLocale

class AdvanceSliderLine(QFrame):
    valueChanged = pyqtSignal(str, float)

    def __init__(self, name: str, default: float, range: tuple[int, int], rangeData: tuple[float, float] = None, nameLength: int = 10, precision: int = 100):
        super().__init__()

        self.name = name
        self.active = True
        self.default = default
        self.guiRange = range
        self.dataRange = rangeData if rangeData else (range[0], range[1])
        self.precision = precision

        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        name = name if len(name) >= nameLength else ' ' * ((nameLength - len(name)) // 2) + name + ' ' * ((nameLength - len(name)) // 2)
        self.label = QLabel(name)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(*range)
        self.slider.setValue(int(default))
        self.edit = QLineEdit()
        self.edit.setText(str(round(default * self.precision) / self.precision))

        validator = QDoubleValidator()
        locale = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
        validator.setLocale(locale)
        self.edit.setValidator(validator)

        self.reset = QPushButton("reset")

        self.hbox.addWidget(self.label, 20)
        self.hbox.addWidget(self.slider, 50)
        self.hbox.addWidget(self.edit, 10)
        self.hbox.addWidget(self.reset, 10)

        self.slider.valueChanged.connect(self.CBsliderChanged)
        self.edit.editingFinished.connect(self.CBeditChanged)
        self.reset.clicked.connect(self.CBreset)

    def setValue(self, val: float) -> None:
        self.active = False
        self.slider.setValue(self.toGui(val))
        self.edit.setText(str(round(val * self.precision) / self.precision))
        self.active = True

    def toGui(self, data: float) -> int:
        u = (data - self.dataRange[0]) / (self.dataRange[1] - self.dataRange[0])
        guiValue = self.guiRange[0] * (1 - u) + self.guiRange[1] * u
        return int(guiValue)

    def toValue(self, data: int) -> float:
        u = (data - self.guiRange[0]) / (self.guiRange[1] - self.guiRange[0])
        value = self.dataRange[0] * (1 - u) + self.dataRange[1] * u
        return value

    def CBsliderChanged(self) -> None:
        if self.active:
            val = round(self.toValue(self.slider.value()) * self.precision) / self.precision
            self.setValue(val)
            self.valueChanged.emit(self.name, val)

    def CBeditChanged(self) -> None:
        if self.active:
            try:
                val = round(float(self.edit.text()) * self.precision) / self.precision
                self.setValue(val)
                self.valueChanged.emit(self.name, val)
            except ValueError:
                print(f"Error: Unable to convert {self.edit.text()} to float.")

    def CBreset(self) -> None:
        if self.active:
            self.setValue(self.default)
            self.valueChanged.emit(self.name, self.default)

# -------------------------------------------------------------------------------------------
