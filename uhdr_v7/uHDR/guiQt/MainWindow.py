# MainWindow.py
from __future__ import annotations
from typing_extensions import Self
from typing import Tuple
from PyQt6.QtWidgets import QFileDialog, QDockWidget, QMainWindow
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction
from numpy import ndarray
from app.Tags import Tags
import preferences.Prefs
from guiQt.AdvanceImageGallery import AdvanceImageGallery
from guiQt.EditorBlock import EditorBlock
from guiQt.InfoSelPrefBlock import InfoSelPrefBlock
from app.ImageFIles import ImageFiles

class MainWindow(QMainWindow):
    # Déclaration des signaux
    dirSelected = pyqtSignal(str)
    requestImages = pyqtSignal(int, int)
    imageSelected = pyqtSignal(int)
    tagChanged = pyqtSignal(tuple, bool)
    scoreChanged = pyqtSignal(int)
    scoreSelectionChanged = pyqtSignal(list)

    # constructor
    def __init__(self: MainWindow, imageFiles: ImageFiles, nbImages: int = 0, tags: dict[Tuple[str, str], bool] = {}):
        super().__init__()

        # attributes
        ## image file management
        self.imageFiles = imageFiles  # Ajout de l'attribut imageFiles

        ## widgets
        self.metaBlock: InfoSelPrefBlock = InfoSelPrefBlock(tags)
        self.editBlock: EditorBlock = EditorBlock()
        self.imageGallery: AdvanceImageGallery = AdvanceImageGallery(nbImages)

        self.metaDock: QDockWidget = QDockWidget("INFO. - SELECTION - PREFERENCES")
        self.metaDock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.metaDock.setWidget(self.metaBlock)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.metaDock)

        self.editDock: QDockWidget = QDockWidget("EDIT")
        self.editDock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.editDock.setWidget(self.editBlock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.editDock)

        self.setCentralWidget(self.imageGallery)

        ## menu
        self.buildFileMenu()

        ## callbacks
        ### from AdvanceImageGallery
        self.imageGallery.requestImages.connect(self.CBrequestImages)
        self.imageGallery.imageSelected.connect(self.CBimageSelected)
        self.metaBlock.tagChanged.connect(self.CBtagChanged)
        self.metaBlock.scoreChanged.connect(self.CBscoreChanged)
        self.metaBlock.scoreSelectionChanged.connect(self.CBscoreSelectionChanged)

        ### from EditorBlock
        self.editBlock.exposureChanged.connect(self.onExposureChanged)
        self.editBlock.contrastScalingChanged.connect(self.onContrastScalingChanged)
        self.editBlock.contrastOffsetChanged.connect(self.onContrastOffsetChanged)
        self.editBlock.lightnessRangeChanged.connect(self.onLightnessRangeChanged)
        self.editBlock.hueShiftChanged.connect(self.onHueShiftChanged)
        self.editBlock.saturationChanged.connect(self.onSaturationChanged)
        self.editBlock.colorExposureChanged.connect(self.onColorExposureChanged)
        self.editBlock.colorContrastChanged.connect(self.onColorContrastChanged)

    # methods
    ## reset
    def resetGallery(self: MainWindow):
        """Reset gallery."""
        print("14")
        self.imageGallery.resetImages()
        
    ## firstPage
    def firstPage(self: MainWindow):
        """Go to first page."""
        print("13")
        self.imageGallery.firstPage()
        
    ## image
    def setGalleryImage(self: Self, index: int, image: ndarray | None) -> None:
        print("13")
        self.imageGallery.setImage(index, image)

    def setNumberImages(self: Self, nbImages: int) -> None:
        print("12")
        self.imageGallery.setNbImages(nbImages)

    def setEditorImage(self: Self, image: ndarray) -> None:
        print("SET IMAGE", image, "?????????????????????????????????????")
        self.editBlock.setImage(image)

    ## tags
    def setTagsImage(self: Self, tags: dict[Tuple[str, str], bool]) -> None:
        print("11")
        self.metaBlock.setTags(tags)

    def resetTags(self: Self) -> None:
        print("10")
        self.metaBlock.resetTags()

    ## info
    def setInfo(self: Self, name: str, path: str, size: tuple[int, int] = (-1, -1), colorSpace: str = '...', type: str = '...', bps: int = -1) -> None:
        print("9")
        self.metaBlock.setInfo(name, path, size, colorSpace, type, bps)

    ## score
    def setScore(self: Self, score: int) -> None:
        print("9")
        self.metaBlock.setScore(score)

    ## prefs
    def setPrefs(self: Self) -> None:
        print("8")
        self.imageGallery.setSize(preferences.Prefs.Prefs.gallerySize)

    ## menu
    def buildFileMenu(self):
        print("7")
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')

        selectDir = QAction('&Select directory', self)        
        selectDir.setShortcut('Ctrl+O')
        selectDir.setStatusTip('[File] select a directory')
        selectDir.triggered.connect(self.CBSelectDir)
        fileMenu.addAction(selectDir)

        selectSave = QAction('&Save', self)        
        selectSave.setShortcut('Ctrl+S')
        selectSave.setStatusTip('[File] saving processpipe metadata')
        selectSave.triggered.connect(lambda x: print('save'))
        fileMenu.addAction(selectSave)

        quit = QAction('&Quit', self)        
        quit.setShortcut('Ctrl+Q')
        quit.setStatusTip('[File] saving updates and quit')
        quit.triggered.connect(lambda x: print('quit'))
        fileMenu.addAction(quit)

    ## callbacks
    ### select dir
    def CBSelectDir(self):
        print("6")
        dirName = QFileDialog.getExistingDirectory(None, 'Select Directory')
        if dirName != "":
            self.dirSelected.emit(dirName)

    def CBrequestImages(self: Self, minIdx: int, maxIdx: int) -> None:
        print("5")
        self.requestImages.emit(minIdx, maxIdx)

    def CBimageSelected(self: Self, idx: int) -> None:
        print("4")
        filename = self.imageFiles.getImagesFilesnames()[idx]
        imageData = self.imageFiles.getImage(filename)
        print(f"Image selected: {filename}, shape: {imageData.shape}, min: {imageData.min()}, max: {imageData.max()}")
        self.setEditorImage(imageData)
        self.imageSelected.emit(idx)


    def CBtagChanged(self, key: tuple[str, str], value: bool) -> None:
        print("3")
        self.tagChanged.emit(key, value)

    def CBscoreChanged(self, value: int) -> None:
        print("2")
        self.scoreChanged.emit(value)

    def CBscoreSelectionChanged(self: Self, scoreSelection: list) -> None:
        print("1")
        self.scoreSelectionChanged.emit(scoreSelection)

    def onExposureChanged(self, value: float):
        print(f'Exposure changed: {value}')
        if self.editBlock.imageWidget.currentImage is not None:
            self.editBlock.imageWidget.adjustExposure(value)

    def onContrastScalingChanged(self, value: float):
        print(f'Contrast scaling changed: {value}')
        if self.editBlock.imageWidget.currentImage is not None:
            self.editBlock.imageWidget.adjustContrastScaling(value)

    def onContrastOffsetChanged(self, value: float):
        print(f'Contrast offset changed: {value}')
        if self.editBlock.imageWidget.currentImage is not None:
            self.editBlock.imageWidget.adjustContrastOffset(value)

    def onLightnessRangeChanged(self, value: tuple):
        print(f'Lightness range changed: {value}')
        if self.editBlock.imageWidget.currentImage is not None:
            print("alalalallalalalala", self.editBlock.imageWidget.currentImage, "lllllllllllllllllllllllllllllllllllllllllll")
            self.editBlock.imageWidget.adjustLightnessRange(value)

    def onHueShiftChanged(self, value: float):
        print(f'Hue Shift changed: {value}')
        if self.editBlock.imageWidget.currentImage is not None:
            self.editBlock.imageWidget.adjustHueShift(value)

    def onSaturationChanged(self, value: float):
        print(f'Saturation changed: {value}')
        if self.editBlock.imageWidget.currentImage is not None:
            self.editBlock.imageWidget.adjustSaturation(value)

    def onColorExposureChanged(self, value: float):
        print(f'Color exposure changed: {value}')
        if self.editBlock.imageWidget.currentImage is not None:
            self.editBlock.imageWidget.adjustColorExposure(value)

    def onColorContrastChanged(self, value: float):
        print(f'Color contrast changed: {value}')
        if self.editBlock.imageWidget.currentImage is not None:
            self.editBlock.imageWidget.adjustColorContrast(value)
