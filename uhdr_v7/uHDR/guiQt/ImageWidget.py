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
        print("SELCURseguyuseghseguyghseghuishiughisehguihseiuhgiuhseg", self.currentImage)
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
        print("riiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii", self.currentImage)
        print(self.currentImage, "oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
        self.updateImage()
        return self.imagePixmap

    def updateImage(self):
        print(self.currentImage, "ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt")
        if self.currentImage is not None:
            height, width, channel = self.currentImage.cData.shape
            bytesPerLine = channel * width
            colorData = self.currentImage.cData
            print(f"Updating image with shape: {colorData.shape}, min: {colorData.min()}, max: {colorData.max()}")
            # print(self.currentImage.cData, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
            qImg = QImage((colorData * 255).astype(np.uint8), width, height, bytesPerLine, QImage.Format.Format_RGB888)
            self.imagePixmap = QPixmap.fromImage(qImg)
            self.label.setPixmap(self.imagePixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        else:
            print("currentImage is None")
        self.resize()


    @staticmethod
    def emptyImageColorData() -> np.ndarray:
        print("orsjgiuhsguishogshigusehgiuhsegsegsegsehsehse")
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
