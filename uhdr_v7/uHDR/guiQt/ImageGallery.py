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
# ImageGallery.py
from __future__ import annotations
from numpy import ndarray
from PyQt6.QtWidgets import QGridLayout, QWidget, QFrame
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QMouseEvent
from guiQt.ImageWidget import ImageWidget

class ImageGallery(QFrame):
    imageSelected = pyqtSignal(int)

    def __init__(self: ImageGallery, size: tuple[int, int]):
        super().__init__()
        self._size: tuple[int, int] = size
        self.imageWidgets: list[ImageWidget] = []

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.imagesLayout = QGridLayout()
        self.setLayout(self.imagesLayout)

        self.buildGrid()

    @property
    def size(self: ImageGallery) -> tuple[int, int]:
        print("25")
        return self._size

    @size.setter
    def size(self: ImageGallery, size: tuple[int, int]) -> None:
        print("24")
        self._size = size
        self.reset()

    def buildGrid(self: ImageGallery) -> None:
        print("23")
        for i in range(self._size[0]): 
            for j in range(self._size[1]):
                iw = ImageWidget()
                self.imageWidgets.append(iw)
                self.imagesLayout.addWidget(iw, i, j)

    def reset(self: ImageGallery) -> None:
        print("22")
        for iw in self.imageWidgets:
            iw.deleteLater()
        self.imageWidgets = []
        self.buildGrid()

    def resetImages(self: ImageGallery) -> None:
        print("21")
        for iw in self.imageWidgets:
            iw.setPixmap(None)

    def setImage(self: ImageGallery, index: int, image: ndarray | None):
        print(image, "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
        self.imageWidgets[index].setPixmap(image)

    def mousePressEvent(self: ImageGallery, event: QMouseEvent):
        print("ccccccccccccccccccccccccc", "20")
        iSelect: int = -1
        if self.childAt(event.pos()):
            if isinstance(self.childAt(event.pos()).parent(), ImageWidget):
                for idx, iw in enumerate(self.imageWidgets):
                    if iw == self.childAt(event.pos()).parent():
                        iSelect = idx  
                        self.imageSelected.emit(iSelect)
                        break
        event.accept()

# -------------------------------------------------------------------------------------------
