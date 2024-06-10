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
# EditorBlock.py
from typing_extensions import Self
from numpy import ndarray
from PyQt6.QtWidgets import QSplitter
from PyQt6.QtCore import Qt, pyqtSignal
from guiQt.Editor import Editor
from guiQt.ImageWidget import ImageWidget

class EditorBlock(QSplitter):
    # Déclaration des signaux
    exposureChanged = pyqtSignal(float)
    contrastScalingChanged = pyqtSignal(float)
    contrastOffsetChanged = pyqtSignal(float)
    lightnessRangeChanged = pyqtSignal(tuple)
    hueShiftChanged = pyqtSignal(float)
    saturationChanged = pyqtSignal(float)
    colorExposureChanged = pyqtSignal(float)
    colorContrastChanged = pyqtSignal(float)

    # constructor
    def __init__(self: Self) -> None:
        super().__init__(Qt.Orientation.Vertical)

        # attributes
        self.imageWidget : ImageWidget = ImageWidget() 
        self.edit : Editor = Editor()

        # Connect signals from Editor to EditorBlock
        self.edit.lightEdit.exposureChanged.connect(self.onExposureChanged)
        self.edit.lightEdit.contrastScalingChanged.connect(self.onContrastScalingChanged)
        self.edit.lightEdit.contrastOffsetChanged.connect(self.onContrastOffsetChanged)
        self.edit.lightEdit.lightnessRangeChanged.connect(self.onLightnessRangeChanged)
        for colorEdit in self.edit.colorEdits:
            colorEdit.hueShiftChanged.connect(self.onHueShiftChanged)
            colorEdit.saturationChanged.connect(self.onSaturationChanged)
            colorEdit.exposureChanged.connect(self.onColorExposureChanged)
            colorEdit.contrastChanged.connect(self.onColorContrastChanged)

        # adding widgets to self (QSplitter)
        self.addWidget(self.imageWidget)
        self.addWidget(self.edit)
        self.setSizes([20,80])

    # methods
    ## setImage
    def setImage(self: Self, image: ndarray | None):
        self.imageWidget.setPixmap(image)

    def onExposureChanged(self, value: float):
        self.exposureChanged.emit(value)

    def onContrastScalingChanged(self, value: float):
        self.contrastScalingChanged.emit(value)

    def onContrastOffsetChanged(self, value: float):
        self.contrastOffsetChanged.emit(value)

    def onLightnessRangeChanged(self, value: tuple):
        self.lightnessRangeChanged.emit(value)

    def onHueShiftChanged(self, value: float):
        self.hueShiftChanged.emit(value)

    def onSaturationChanged(self, value: float):
        self.saturationChanged.emit(value)

    def onColorExposureChanged(self, value: float):
        self.colorExposureChanged.emit(value)

    def onColorContrastChanged(self, value: float):
        self.colorContrastChanged.emit(value)
