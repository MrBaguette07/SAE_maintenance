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
    highlightsChanged = pyqtSignal(float)
    shadowsChanged = pyqtSignal(float)
    whitesChanged = pyqtSignal(float)
    blacksChanged = pyqtSignal(float)
    mediumsChanged = pyqtSignal(float)

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
        
        for colorEdit in self.edit.colorEdits:
            colorEdit.hueShiftChanged.connect(self.hueShiftChanged)
            colorEdit.saturationChanged.connect(self.saturationChanged)
            colorEdit.exposureChanged.connect(self.colorExposureChanged)
            colorEdit.contrastChanged.connect(self.colorContrastChanged)

        # adding widgets to self (QSplitter)
        self.addWidget(self.imageWidget)
        self.addWidget(self.edit)
        self.setSizes([20, 80])

    # methods
    def setImage(self: Self, image: ndarray | None):
        self.imageWidget.setPixmap(image)
