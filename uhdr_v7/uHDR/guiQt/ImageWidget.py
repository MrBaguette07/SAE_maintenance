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
# -----------------------------------------------------------------------------
# ImageWidget.py
from typing_extensions import Self
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap, QImage, QResizeEvent
from PyQt6.QtCore import Qt
import numpy as np
from core.image import Image

class ImageWidget(QWidget):
    def __init__(self: Self, colorData: np.ndarray | None = None) -> None:
        super().__init__()
        self.label: QLabel = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        if colorData is None:
            colorData = ImageWidget.emptyImageColorData()
        self.currentImage = Image(colorData)
        self.setPixmap(colorData)

    def resize(self: Self) -> None:
        self.label.resize(self.size())
        self.label.setPixmap(self.imagePixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def resizeEvent(self: Self, event: QResizeEvent) -> None:
        self.resize()
        super().resizeEvent(event)

    def setPixmap(self: Self, colorData: np.ndarray | None = None) -> QPixmap:
        if colorData is None:
            colorData = ImageWidget.emptyImageColorData()
        self.currentImage = Image(colorData)
        self.updateImage()
        return self.imagePixmap

    def updateImage(self):
        if self.currentImage is not None:
            height, width, channel = self.currentImage.cData.shape
            bytesPerLine = channel * width
            colorData = self.currentImage.cData.clip(0, 1)
            print(f"Updating image with shape: {colorData.shape}, min: {colorData.min()}, max: {colorData.max()}")
            qImg = QImage((colorData * 255).astype(np.uint8), width, height, bytesPerLine, QImage.Format.Format_RGB888)
            self.imagePixmap = QPixmap.fromImage(qImg)
            self.label.setPixmap(self.imagePixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.resize()

    def setQPixmap(self: Self, qPixmap: QPixmap) -> None:
        self.imagePixmap = qPixmap
        self.resize()

    @staticmethod
    def emptyImageColorData() -> np.ndarray:
        return np.ones((90, 160, 3)) * (220 / 255)

    # Méthodes d'ajustement
    def adjustExposure(self, value: float):
        if self.currentImage:
            self.currentImage.adjustExposure(value)
            self.updateImage()

    def adjustContrastScaling(self, value: float):
        if self.currentImage:
            self.currentImage.adjustContrastScaling(value)
            self.updateImage()

    def adjustContrastOffset(self, value: float):
        if self.currentImage:
            self.currentImage.adjustContrastOffset(value)
            self.updateImage()

    def adjustLightnessRange(self, value: tuple):
        if self.currentImage:
            self.currentImage.adjustLightnessRange(value)
            self.updateImage()

    def adjustHueShift(self, value: float):
        if self.currentImage:
            self.currentImage.adjustHueShift(value)
            self.updateImage()

    def adjustSaturation(self, value: float):
        if self.currentImage:
            self.currentImage.adjustSaturation(value)
            self.updateImage()

    def adjustColorExposure(self, value: float):
        if self.currentImage:
            self.currentImage.adjustColorExposure(value)
            self.updateImage()

    def adjustColorContrast(self, value: float):
        if self.currentImage:
            self.currentImage.adjustColorContrast(value)
            self.updateImage()


# -------------------------------------------------------------------------------------------
if __name__ == '__main__':
    from matplotlib.pyplot import imread
    import sys
    from PyQt6.QtWidgets import QApplication
    img : np.ndarray = imread('C:/Users/rcozo/Dropbox/dev/copoc/images/maximus/4.jpg')/255
    app : QApplication = QApplication(sys.argv)
    iW : ImageWidget = ImageWidget()
    iW.setMinimumHeight(55)
    iW.show()

    sys.exit(app.exec())