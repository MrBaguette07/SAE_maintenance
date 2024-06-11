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
# Editor.py
from typing_extensions import Self
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtCore import pyqtSignal
from guiQt.LightBlockScroll import LightBlockScroll
from guiQt.ColorBlockScroll import ColorBlockScroll

class Editor(QTabWidget):
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
        super().__init__()

        # attributes
        self.lightEdit: LightBlockScroll = LightBlockScroll() 
        self.nbColorEditor: int = 5       
        self.colorEdits: list[ColorBlockScroll] = []
        for i in range(self.nbColorEditor): 
            colorEdit = ColorBlockScroll()
            self.colorEdits.append(colorEdit)

        # QTabWidget setup
        self.setTabPosition(QTabWidget.TabPosition.East)
        self.setMovable(True)

        # add widgets
        self.addTab(self.lightEdit, "Light")
        for i in range(self.nbColorEditor): 
            self.addTab(self.colorEdits[i], "Color " + str(i))
        
        # Connect signals to Editor
        self.lightEdit.exposureChanged.connect(self.exposureChanged)
        self.lightEdit.contrastScalingChanged.connect(self.contrastScalingChanged)
        self.lightEdit.contrastOffsetChanged.connect(self.contrastOffsetChanged)
        self.lightEdit.lightnessRangeChanged.connect(self.lightnessRangeChanged)
        for colorEdit in self.colorEdits:
            colorEdit.hueShiftChanged.connect(self.hueShiftChanged)
            colorEdit.saturationChanged.connect(self.saturationChanged)
            colorEdit.exposureChanged.connect(self.colorExposureChanged)
            colorEdit.contrastChanged.connect(self.colorContrastChanged)
