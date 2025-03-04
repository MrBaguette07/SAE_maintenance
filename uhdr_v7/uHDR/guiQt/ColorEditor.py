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
from typing_extensions import Self
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout,QPushButton, QLabel, QLineEdit, QSlider, QCheckBox
from PyQt6.QtGui import QDoubleValidator, QIntValidator 
from PyQt6.QtCore import Qt, pyqtSignal, QLocale
from guiQt.AdvanceSliderLine import AdvanceSliderLine

# ------------------------------------------------------------------------------------------
# --- class ColorEditor (QFrame) ------------------------------------------------------
# ------------------------------------------------------------------------------------------

class ColorEditor(QFrame):
    # Declaration of signals
    hueShiftChanged = pyqtSignal(float)
    saturationChanged = pyqtSignal(float)
    exposureChanged = pyqtSignal(float)
    contrastChanged = pyqtSignal(float)

    # constructor
    def __init__(self : Self) -> None:
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # attributes

        ## layout and widget
        self.topLayout : QVBoxLayout = QVBoxLayout()
        self.setLayout(self.topLayout)

        self.hueShift = AdvanceSliderLine('hue shift', 0.0, (-180, 180))
        self.saturation = AdvanceSliderLine('saturation', 0.0, (-100, 100))
        self.exposure = AdvanceSliderLine('exposure', 0, (-300, 300), (-3, +3)) # -3,+3 0.01
        self.contrast = AdvanceSliderLine('contrast', 0.0, (-100, 100))

        ## Connect signals to slots
        self.hueShift.valueChanged.connect(self.onHueShiftChanged)
        self.saturation.valueChanged.connect(self.onSaturationChanged)
        self.exposure.valueChanged.connect(self.onExposureChanged)
        self.contrast.valueChanged.connect(self.onContrastChanged)

        ## add widget to layout
        self.topLayout.addWidget(self.hueShift)
        self.topLayout.addWidget(self.saturation)
        self.topLayout.addWidget(self.exposure)
        self.topLayout.addWidget(self.contrast)

    def onHueShiftChanged(self, str: str, value: float):
        """
        Returns the signal when the value of Hue change
        
        Args :
            str (bool)
            value (float, required)
        """

        self.hueShiftChanged.emit(value)

    def onSaturationChanged(self, str: str, value: float):
        """
        Returns the signal when the value of Saturation change

        Args :
            str (bool)
            value (float, required)
        """

        self.saturationChanged.emit(value)

    def onExposureChanged(self, str: str, value: float):
        """
        Returns the signal when the value of Exposure change

        Args :
            str (bool)
            value (float, required)
        """

        self.exposureChanged.emit(value)

    def onContrastChanged(self, str: str, value: float):
        """
        Returns the signal when the value of Contrast change

        Args :
            str (bool)
            value (float, required)
        """
        
        self.contrastChanged.emit(value)


# ------------------------------------------------------------------------------------------
        

