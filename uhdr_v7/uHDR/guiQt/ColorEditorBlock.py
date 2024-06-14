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
from PyQt6.QtWidgets import QFrame, QVBoxLayout
from PyQt6.QtGui import QDoubleValidator, QIntValidator 
from PyQt6.QtCore import Qt, pyqtSignal, QLocale

from guiQt.LchSelector import LchSelector
from guiQt.ColorEditor import ColorEditor
from guiQt.MemoGroup import MemoGroup

# ------------------------------------------------------------------------------------------
# --- class ColorEditor (QFrame) ------------------------------------------------------
# ------------------------------------------------------------------------------------------

class ColorEditorBlock(QFrame):
    # Declaration of signals
    hueShiftChanged = pyqtSignal(float)
    saturationChanged = pyqtSignal(float)
    exposureChanged = pyqtSignal(float)
    contrastChanged = pyqtSignal(float)

    hueRangeChanged = pyqtSignal(tuple)
    chromaRangeChanged = pyqtSignal(tuple)
    lightnessRangeChanged = pyqtSignal(tuple)

    activeColorsChanged: pyqtSignal = pyqtSignal(bool)

    def __init__(self : Self) -> None:
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # attributes
        self.active : bool = True

        # layout and widgets
        self.topLayout : QVBoxLayout = QVBoxLayout()
        self.setLayout(self.topLayout)

        self.selector : LchSelector = LchSelector()
        self.editor : ColorEditor = ColorEditor()

        ## Connect signals from ColorEditor to ColorEditorBlock
        self.editor.hueShiftChanged.connect(self.hueShiftChanged)
        self.editor.saturationChanged.connect(self.saturationChanged)
        self.editor.exposureChanged.connect(self.exposureChanged)
        self.editor.contrastChanged.connect(self.contrastChanged)

        self.selector.hueRangeChanged.connect(self.hueRangeChanged)
        self.selector.chromaRangeChanged.connect(self.chromaRangeChanged)
        self.selector.lightnessRangeChanged.connect(self.lightnessRangeChanged)

        self.selector.activeColorsChanged.connect(self.onActiveColorsChanged)

        ## add to layout
        self.topLayout.addWidget(self.selector)
        self.topLayout.addWidget(self.editor)

        #self.topLayout.addWidget(self.memory)
    
    def onActiveColorsChanged(self: Self, value: bool):
        """
        Transforms the different modules by activating or deactivating them according to the parameter (value)

        Args :
            value (bool, required)
        """

        # Transforme le bouton/slider de hueshift vers la valeur d'activation ou désactivation
        self.editor.hueShift.slider.setEnabled(value)
        self.editor.hueShift.edit.setEnabled(value)
        self.editor.hueShift.reset.setEnabled(value)

        # Transforme le bouton/slider de saturation vers la valeur d'activation ou désactivation
        self.editor.saturation.slider.setEnabled(value)
        self.editor.saturation.edit.setEnabled(value)
        self.editor.saturation.reset.setEnabled(value)

        # Transforme le bouton/slider de exposure vers la valeur d'activation ou désactivation
        self.editor.exposure.slider.setEnabled(value)
        self.editor.exposure.edit.setEnabled(value)
        self.editor.exposure.reset.setEnabled(value)

        # Transforme le bouton/slider de contrast vers la valeur d'activation ou désactivation
        self.editor.contrast.slider.setEnabled(value)
        self.editor.contrast.edit.setEnabled(value)
        self.editor.contrast.reset.setEnabled(value)

        # Transforme le bouton/slider de colors vers la valeur d'activation ou désactivation
        self.activeColorsChanged.emit(value)

