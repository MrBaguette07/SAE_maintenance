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
# LightBlockScroll.py
from typing_extensions import Self
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal
from guiQt.LightBlock import LightBlock

class LightBlockScroll(QScrollArea):
    # Déclaration des signaux
    exposureChanged = pyqtSignal(float)
    contrastScalingChanged = pyqtSignal(float)
    contrastOffsetChanged = pyqtSignal(float)
    lightnessRangeChanged = pyqtSignal(tuple)
    highlightsChanged = pyqtSignal(float)
    shadowsChanged = pyqtSignal(float)
    whitesChanged = pyqtSignal(float)
    blacksChanged = pyqtSignal(float)
    mediumsChanged = pyqtSignal(float)

    activeContrastChanged = pyqtSignal(bool)
    activeExposureChanged = pyqtSignal(bool)
    activeLightnessChanged = pyqtSignal(bool)

    loadJsonChanged: pyqtSignal = pyqtSignal(list)

    # autoClickedExposure: pyqtSignal = pyqtSignal(bool)

    # constructor
    def __init__(self : Self) -> None:
        super().__init__()

        ## lightblock widget
        self.light = LightBlock()
        self.light.setMinimumSize(500, 1500)

        ## Scroll Area Properties
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.light)

        # Connect signals from LightBlock to LightBlockScroll
        self.light.exposure.valueChanged.connect(self.onExposureChanged)
        self.light.contrast.scalingChanged.connect(self.onContrastScalingChanged)
        self.light.contrast.activeContrastChanged.connect(self.onActiveContrastChanged)
        self.light.activeExposureChanged.connect(self.onActiveExposureChanged)
        # self.light.autoClickedExposure.connect(self.autoClickedExposure)
        # self.light.contrast.loadJsonChanged.emit(self.onLoadJsonChanged)

        self.light.contrast.offsetChanged.connect(self.onContrastOffsetChanged)
        self.light.contrast.lightnessRangeChanged.connect(self.onLightnessRangeChanged)
        self.light.curve.highlightsChanged.connect(self.onHighlightsChanged)
        self.light.curve.shadowsChanged.connect(self.onShadowsChanged)
        self.light.curve.whitesChanged.connect(self.onWhitesChanged)
        self.light.curve.blacksChanged.connect(self.onBlacksChanged)
        self.light.curve.mediumsChanged.connect(self.onMediumsChanged)
        self.light.curve.activeLightnessChanged.connect(self.onActiveLightnessChanged)

    def onActiveLightnessChanged(self, value: bool):
        """
        Returns the signal of the activation state of lightness
        
        Args :
            value (bool, Required)
        """
        self.activeLightnessChanged.emit(value)

    def onLoadJsonChanged(self, value: list):
        """
        Returning the signal after the loading of a json file
        
        Args :
            value (list, Required)
        """
        self.loadJsonChanged.emit(value)

    def onExposureChanged(self, value: float):
        """
        Returns the signal when the slider of Exposure change
        
        Args :
            value (float, Required)
        """
        self.exposureChanged.emit(value)

    def onContrastScalingChanged(self, value: float):
        """
        Returns the signal of Contrast when the slider of Scaling change
        
        Args :
            value (float, Required)
        """
        self.contrastScalingChanged.emit(value)

    def onContrastOffsetChanged(self, value: float):
        """
        Returns the signal of Contrast when the slider of Offset change
        
        Args :
            value (float, Required)
        """
        self.contrastOffsetChanged.emit(value)

    def onLightnessRangeChanged(self, value: tuple):
        """
        Returns the signal when one of the slider of Lightness change
        
        Args :
            value (tuple [min,max], Required)
        """
        self.lightnessRangeChanged.emit(value)

    def onHighlightsChanged(self, value: float):
        """
        Returns the signal when the slider change (curve)
        
        Args :
            value (float, Required)
        """
        self.highlightsChanged.emit(value)

    def onShadowsChanged(self, value: float):
        """ 
        Returns the signal when the slider change (curve)
        
        Args :
            value (float, Required)
        """
        self.shadowsChanged.emit(value)

    def onWhitesChanged(self, value: float):
        """
        Returns the signal when the slider change (curve)
        
        Args :
            value (float, Required)
        """
        self.whitesChanged.emit(value)

    def onBlacksChanged(self, value: float):
        """
        Returns the signal when the slider change (curve)
        
        Args :
            value (float, Required)
        """
        self.blacksChanged.emit(value)
    
    def onMediumsChanged(self, value: float):
        """
        Returns the signal when the slider change (curve)
        
        Args :
            value (float, Required)
        """
        self.mediumsChanged.emit(value)

    def onActiveContrastChanged(self, value: bool):
        """
        Returns the signal when the slider change (curve)
        
        Args :
            value (bool, Required)
        """
        self.activeContrastChanged.emit(value)
    
    def onActiveExposureChanged(self, value: bool):
        """ 
        Returns the signal when the slider change (curve)
        
        Args :
            value (bool, Required)
        """
        self.activeExposureChanged.emit(value)

