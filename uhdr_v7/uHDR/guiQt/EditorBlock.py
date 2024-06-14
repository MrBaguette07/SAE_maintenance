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
    hueShiftChanged = pyqtSignal(float, int)
    saturationChanged = pyqtSignal(float, int)
    colorExposureChanged = pyqtSignal(float, int)
    colorContrastChanged = pyqtSignal(float, int)
    highlightsChanged = pyqtSignal(float)
    shadowsChanged = pyqtSignal(float)
    whitesChanged = pyqtSignal(float)
    blacksChanged = pyqtSignal(float)
    mediumsChanged = pyqtSignal(float)

    hueRangeChanged = pyqtSignal(tuple, int)
    chromaRangeChanged = pyqtSignal(tuple, int)
    lightness2RangeChanged = pyqtSignal(tuple, int)

    activeContrastChanged = pyqtSignal(bool)
    activeExposureChanged = pyqtSignal(bool)
    activeLightnessChanged = pyqtSignal(bool)
    activeColorsChanged = pyqtSignal(bool, int)

    loadJsonChanged: pyqtSignal = pyqtSignal(list)

    # autoClickedExposure: pyqtSignal = pyqtSignal(bool)

    def __init__(self: Self) -> None:
        super().__init__(Qt.Orientation.Vertical)

        # attributes
        self.imageWidget: ImageWidget = ImageWidget()
        self.edit: Editor = Editor()

        # Connect signals from Editor to EditorBlock
        self.edit.lightEdit.exposureChanged.connect(self.exposureChanged)
        self.edit.lightEdit.contrastScalingChanged.connect(self.contrastScalingChanged)
        self.edit.lightEdit.contrastOffsetChanged.connect(self.contrastOffsetChanged)
        self.edit.lightEdit.lightnessRangeChanged.connect(self.lightnessRangeChanged)
        self.edit.lightEdit.highlightsChanged.connect(self.highlightsChanged)
        self.edit.lightEdit.shadowsChanged.connect(self.shadowsChanged)
        self.edit.lightEdit.whitesChanged.connect(self.whitesChanged)
        self.edit.lightEdit.blacksChanged.connect(self.blacksChanged)
        self.edit.lightEdit.mediumsChanged.connect(self.mediumsChanged)

        self.edit.lightEdit.activeContrastChanged.connect(self.activeContrastChanged)
        self.edit.lightEdit.activeExposureChanged.connect(self.activeExposureChanged)
        self.edit.lightEdit.activeLightnessChanged.connect(self.activeLightnessChanged)

        # self.edit.lightEdit.autoClickedExposure.connect(self.autoClickedExposure)
        
        # Loop to declare signals by callbacks
        index = 0
        for colorEdit in self.edit.colorEdits:
            self._connect_color_signals(colorEdit, index)
            self._connect_active_signals(colorEdit, index)
            index += 1

        # adding widgets to self (QSplitter)
        self.addWidget(self.imageWidget)
        self.addWidget(self.edit)
        self.setSizes([20, 80])

    def _connect_color_signals(self: Self, colorEdit: float, index: int):
        """
        Transformation of a signal with 1 parameter to 2 parameters
        
        Args :
            colorEdit (float, Required)
            index (int, required)
        """
    
        colorEdit.hueShiftChanged.connect(lambda value, idx=index: self.hueShiftChanged.emit(value, idx))
        colorEdit.saturationChanged.connect(lambda value, idx=index: self.saturationChanged.emit(value, idx))
        colorEdit.exposureChanged.connect(lambda value, idx=index: self.colorExposureChanged.emit(value, idx))
        colorEdit.contrastChanged.connect(lambda value, idx=index: self.colorContrastChanged.emit(value, idx))

        colorEdit.hueRangeChanged.connect(lambda value, idx=index: self.hueRangeChanged.emit(value, idx))
        colorEdit.chromaRangeChanged.connect(lambda value, idx=index: self.chromaRangeChanged.emit(value, idx))
        colorEdit.lightnessRangeChanged.connect(lambda value, idx=index: self.lightness2RangeChanged.emit(value, idx))
    
    def _connect_active_signals(self: Self, colorEdit: bool, index: int):
        """
        Transformation of a signal with 1 parameter to 2 parameters

        Args :
            colorEdit (bool, Required)
            index (int, required)
        """

        colorEdit.activeColorsChanged.connect(lambda value, idx=index: self.activeColorsChanged.emit(value, idx))

    # methods
    def setImage(self: Self, image: ndarray | None):
        self.imageWidget.setPixmap(image)
