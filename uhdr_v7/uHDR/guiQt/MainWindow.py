# MainWindow.py
from __future__ import annotations
from typing_extensions import Self
from typing import Tuple
from PyQt6.QtWidgets import QFileDialog, QDockWidget, QMainWindow
from PyQt6.QtCore import pyqtSignal, Qt, pyqtSlot
from PyQt6.QtGui import QAction
from numpy import ndarray
from app.Tags import Tags
import preferences.Prefs
from guiQt.AdvanceImageGallery import AdvanceImageGallery
from guiQt.EditorBlock import EditorBlock
from guiQt.InfoSelPrefBlock import InfoSelPrefBlock

debug = False

class MainWindow(QMainWindow):
    # Déclaration des signaux
    dirSelected = pyqtSignal(str)
    requestImages = pyqtSignal(int, int)
    imageSelected = pyqtSignal(int)
    tagChanged = pyqtSignal(tuple, bool)
    scoreChanged = pyqtSignal(int)
    scoreSelectionChanged = pyqtSignal(list)

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
    

    # constructor
    
    def __init__(self: MainWindow, nbImages: int = 0, tags : dict[Tuple[str,str], bool] = {}) -> None:
        super().__init__()

        # attributes
        ## widgets
        self.metaBlock : InfoSelPrefBlock =InfoSelPrefBlock(tags)

        self.editBlock : EditorBlock =EditorBlock()
        self.imageGallery : AdvanceImageGallery  = AdvanceImageGallery(nbImages)


        self.metaDock : QDockWidget = QDockWidget("INFO. - SELECTION - PREFERENCES")
        self.metaDock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.metaDock.setWidget(self.metaBlock)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.metaDock)

        self.editDock : QDockWidget = QDockWidget("EDIT")
        self.editDock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.editDock.setWidget(self.editBlock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.editDock)

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
        self.editBlock.exposureChanged.connect(self.exposureChanged)
        self.editBlock.contrastScalingChanged.connect(self.contrastScalingChanged)
        self.editBlock.contrastOffsetChanged.connect(self.contrastOffsetChanged)
        self.editBlock.lightnessRangeChanged.connect(self.lightnessRangeChanged)
        self.editBlock.hueShiftChanged.connect(self.hueShiftChanged)
        self.editBlock.saturationChanged.connect(self.saturationChanged)
        self.editBlock.colorExposureChanged.connect(self.colorExposureChanged)
        self.editBlock.colorContrastChanged.connect(self.colorContrastChanged)
        self.editBlock.highlightsChanged.connect(self.highlightsChanged)
        self.editBlock.shadowsChanged.connect(self.shadowsChanged)
        self.editBlock.whitesChanged.connect(self.whitesChanged)
        self.editBlock.blacksChanged.connect(self.blacksChanged)
        self.editBlock.mediumsChanged.connect(self.mediumsChanged)

        self.editBlock.hueRangeChanged.connect(self.hueRangeChanged)
        self.editBlock.chromaRangeChanged.connect(self.chromaRangeChanged)
        self.editBlock.lightness2RangeChanged.connect(self.lightness2RangeChanged)

        self.editBlock.activeContrastChanged.connect(self.activeContrastChanged)
        self.editBlock.activeExposureChanged.connect(self.activeExposureChanged)
        self.editBlock.activeLightnessChanged.connect(self.activeLightnessChanged)
        self.editBlock.activeColorsChanged.connect(self.activeColorsChanged)

        # self.editBlock.autoClickedExposure.connect(self.autoClickedExposure)

        # self.editBlock.loadJsonChanged.emit(self.loadJsonChanged)

    # methods
    ## reset

    def resetGallery(self:MainWindow):
        """resetGallery"""
        
        if debug: print(f'MainWindows.resetGallery()')

        self.imageGallery.gallery.resetImages()
        
    ## firstPage
    def firstPage(self: MainWindow):
        """go to first page."""

        if debug: print(f'MainWindows.firstPage()')
        
        self.imageGallery.firstPage()
        
    
    ## image
    def setGalleryImage(self: Self, index: int, image: ndarray|None) -> None:
        """send the image of global index to image gallery"""
        if debug: print(f'MainWindows.setGalleryImage(index={index}, image= ...)')
        self.imageGallery.setImage(index, image)

    def setNumberImages(self: Self, nbImages: int) -> None:
        self.imageGallery.setNbImages(nbImages)

    def setEditorImage(self: Self, image: ndarray) -> None:
        self.editBlock.setImage(image)

    ## tags
    def setTagsImage(self: Self, tags: dict[Tuple[str,str], bool]) -> None :
        self.metaBlock.setTags(tags)

    def resetTags(self: Self) -> None:
        self.metaBlock.resetTags()

    ## info
    def setInfo(self: Self, name: str, path: str, size : tuple[int,int] =(-1,-1), colorSpace : str = '...', type: str ='...', bps : int =-1) -> None:
        self.metaBlock.setInfo(name, path, size, colorSpace, type, bps )

    ## score
    def setScore(self: Self, score : int) -> None:
        self.metaBlock.setScore(score)

    ## prefs
    def setPrefs(self:Self) -> None:
        self.imageGallery.setSize(preferences.Prefs.Prefs.gallerySize)
    
    ## menu
    def buildFileMenu(self):
        menubar = self.menuBar()# get menubar
        fileMenu = menubar.addMenu('&File')# file menu

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
    ## -------------------------------------------------------------------
    ### select dir
    def CBSelectDir(self):
        dirName = QFileDialog.getExistingDirectory(None, 'Select Directory')
        if dirName != "": self.dirSelected.emit(dirName)

    ## -------------------------------------------------------------------
    ### requestImages
    def CBrequestImages(self: Self, minIdx: int, maxIdx: int) -> None:
        if debug : print(f'MainWindow.CBrequestImages({minIdx},{maxIdx})')
        self.requestImages.emit(minIdx, maxIdx)

    ## -------------------------------------------------------------------
    ### image selected
    def CBimageSelected(self: Self, idx: int) -> None:
        if debug : print(f'MainWindow.CBimageSelected({idx})')
        self.imageSelected.emit(idx)

    # -----------------------------------------------------------------
    def CBtagChanged(self, key: tuple[str, str], value : bool) -> None:
        if debug : print(f'guiQt.MainWindow.CBtagChanged({key},{value}) > emit !')
        self.tagChanged.emit(key,value)
    # -----------------------------------------------------------------
    def CBscoreChanged(self, value : int) -> None:
        if debug : print(f'guiQt.MainWindow.CBscoreChanged({value}) > emit !')
        self.scoreChanged.emit(value)
    # -----------------------------------------------------------------
    def CBscoreSelectionChanged(self: Self, scoreSelection: list) -> None:
        if debug : print(f'guiQt.MainWindow.CBscoreSelectionChanged({scoreSelection})') 
        self.scoreSelectionChanged.emit(scoreSelection)