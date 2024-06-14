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
    # Declaration of signals
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

    hueRangeChanged = pyqtSignal(tuple)
    chromaRangeChanged = pyqtSignal(tuple)
    lightness2RangeChanged = pyqtSignal(tuple)

    activeContrastChanged = pyqtSignal(bool)
    activeExposureChanged = pyqtSignal(bool)
    activeLightnessChanged = pyqtSignal(bool)
    activeColorsChanged: pyqtSignal = pyqtSignal(bool)

    loadJsonChanged: pyqtSignal = pyqtSignal(list)

    # autoClickedExposure: pyqtSignal = pyqtSignal(bool)


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
        self.lightEdit.highlightsChanged.connect(self.highlightsChanged)
        self.lightEdit.shadowsChanged.connect(self.shadowsChanged)
        self.lightEdit.whitesChanged.connect(self.whitesChanged)
        self.lightEdit.blacksChanged.connect(self.blacksChanged)
        self.lightEdit.mediumsChanged.connect(self.mediumsChanged)

        # self.lightEdit.autoClickedExposure.connect(self.autoClickedExposure)

        self.lightEdit.activeContrastChanged.connect(self.activeContrastChanged)
        self.lightEdit.activeExposureChanged.connect(self.activeExposureChanged)
        self.lightEdit.activeLightnessChanged.connect(self.activeLightnessChanged)
        
        for colorEdit in self.colorEdits:
            colorEdit.hueShiftChanged.connect(self.hueShiftChanged)
            colorEdit.saturationChanged.connect(self.saturationChanged)
            colorEdit.exposureChanged.connect(self.colorExposureChanged)
            colorEdit.contrastChanged.connect(self.colorContrastChanged)

            colorEdit.hueRangeChanged.connect(self.hueRangeChanged)
            colorEdit.chromaRangeChanged.connect(self.chromaRangeChanged)
            colorEdit.lightnessRangeChanged.connect(self.lightness2RangeChanged)

            colorEdit.activeColorsChanged.connect(self.activeColorsChanged)

            
        