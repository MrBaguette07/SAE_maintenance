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
from __future__ import annotations

from numpy import ndarray, copy
from app.Jexif import Jexif

from PyQt6.QtCore import pyqtSignal
import preferences.Prefs
from guiQt.MainWindow import MainWindow
from app.ImageFIles import ImageFiles
from app.Tags import Tags
from app.SelectionMap import SelectionMap
from hdrCore import coreC, utils, processing
from core.image import Image  # Assurez-vous d'importer la classe Image appropriée
from core.colourSpace import ColorSpace  # Import ColorSpace as well

# ------------------------------------------------------------------------------------------
# --- class App ----------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
debug : bool = True
class App:
    # static attributes

    # constructor
    def __init__(self: App) -> None:
        """uHDR v7 application"""
        # loading preferences
        preferences.Prefs.Prefs.load()

        ## -----------------------------------------------------
        ## ------------         attributes          ------------
        ## -----------------------------------------------------        
        
        ## image file management
        self.imagesManagement : ImageFiles = ImageFiles()
        self.imagesManagement.imageLoaded.connect(self.CBimageLoaded)
        self.imagesManagement.setPrefs()
        self.imagesManagement.checkExtra()
        nbImages : int = self.imagesManagement.setDirectory(preferences.Prefs.Prefs.currentDir)

        # read image tags in directory
        allTagsInDir : dict[str, dict[str,bool]] =  Tags.aggregateTagsFiles(preferences.Prefs.Prefs.currentDir,preferences.Prefs.Prefs.extraPath)
        
        # merge with default tags from preferences
        self.tags : Tags = Tags(Tags.aggregateTagsData([preferences.Prefs.Prefs.tags, allTagsInDir]))
        
        ## selection
        self.selectionMap :  SelectionMap = SelectionMap(self.imagesManagement.getImagesFilesnames())

        ## current selected image
        self.selectedImageIdx : int | None = None
        self.processPipe: dict | None = None
        self.metadataProcess: dict | None = None
        self.metaImage: Image | None = None
        self.originalMeta: dict | None = None
        self.saveMeta: dict | None = None
        self.disabledContent: list = [{'exposure': True},{'contrast': True},{'lightness': True},[True,True,True,True,True]]

        ## to store original images
        self.originalImages: dict[str, Image] = {}

        ## -----------------------------------------------------
        ## ------------             gui             ------------
        ## -----------------------------------------------------

        self.mainWindow : MainWindow = MainWindow(nbImages, self.tags.toGUI())
        self.mainWindow.showMaximized()
        self.mainWindow.show()

        ## callbacks
        self.mainWindow.dirSelected.connect(self.CBdirSelected)
        self.mainWindow.requestImages.connect(self.CBrequestImages)
        self.mainWindow.imageSelected.connect(self.CBimageSelected)

        self.mainWindow.tagChanged.connect(self.CBtagChanged)
        self.mainWindow.scoreChanged.connect(self.CBscoreChanged)
        self.mainWindow.scoreSelectionChanged.connect(self.CBscoreSelectionChanged)

        self.mainWindow.exposureChanged.connect(self.onExposureChanged)
        self.mainWindow.contrastScalingChanged.connect(self.onContrastScalingChanged)
        
        # Offset is not used for the moment, as the function in the core is not defined yet
        # self.mainWindow.contrastOffsetChanged.connect(self.onContrastOffsetChanged)

        self.mainWindow.lightnessRangeChanged.connect(self.onLightnessRangeChanged)
        self.mainWindow.hueShiftChanged.connect(self.onHueShiftChanged)
        self.mainWindow.saturationChanged.connect(self.onSaturationChanged)
        self.mainWindow.colorExposureChanged.connect(self.onColorExposureChanged)
        self.mainWindow.colorContrastChanged.connect(self.onColorContrastChanged)
        self.mainWindow.highlightsChanged.connect(self.onHighlightsChanged)
        self.mainWindow.shadowsChanged.connect(self.onShadowsChanged)
        self.mainWindow.whitesChanged.connect(self.onWhitesChanged)
        self.mainWindow.blacksChanged.connect(self.onBlacksChanged)
        self.mainWindow.mediumsChanged.connect(self.onMediumsChanged)

        self.mainWindow.hueRangeChanged.connect(self.onHueRangeChanged)
        self.mainWindow.chromaRangeChanged.connect(self.onChromaRangeChanged)
        self.mainWindow.lightness2RangeChanged.connect(self.onLightness2RangeChanged)

        self.mainWindow.activeContrastChanged.connect(self.onActiveContrastChanged)
        self.mainWindow.activeExposureChanged.connect(self.onActiveExposureChanged)
        self.mainWindow.activeLightnessChanged.connect(self.onActiveLightnessChanged)
        self.mainWindow.activeColorsChanged.connect(self.onActiveColorsChanged)

        # self.mainWindow.autoClickedExposure.connect(self.onAutoClickedExposure)

        self.mainWindow.setPrefs()

    # methods
    # -----------------------------------------------------------------

    ##  getImageRangeIndex
    ## ----------------------------------------------------------------
    def getImageRangeIndex(self: App) -> tuple[int,int]: 
        """return the index range (min index, max index) of images displayed by the gallery."""

        return self.mainWindow.imageGallery.getImageRangeIndex()

    ##  update
    ## ----------------------------------------------------------------
    def update(self: App) -> None:
        """call to update gallery after selection changed or directory changed."""
        # number of image in current pages 
        minIdx, maxIdx = self.getImageRangeIndex()
        self.mainWindow.setNumberImages(self.selectionMap.getSelectedImageNumber()) 
        self.mainWindow.setNumberImages(maxIdx - minIdx) 
        self.CBrequestImages(minIdx, maxIdx)

    ## -----------------------------------------------------------------------------------------------------
    ## app logic: callbacks 
    ## -----------------------------------------------------------------------------------------------------

    #### select new directory
    #### -----------------------------------------------------------------
    def CBdirSelected(self: App, path:str) -> None:
        """callback: called when directory is selected."""

        # ------------- DEBUG -------------
        if debug : 
            print(f'App.CBdirSelected({path})')
        # ------------- ------ -------------  

        self.imagesManagement.setDirectory(path)
        self.selectionMap.setImageNames(self.imagesManagement.getImagesFilesnames())
        self.selectionMap.selectAll()

        # reset gallery 
        self.mainWindow.resetGallery()
        self.mainWindow.setNumberImages(self.imagesManagement.getNbImages())
        self.mainWindow.firstPage()

    #### request image: zoom or page changed
    #### -----------------------------------------------------------------
    def CBrequestImages(self: App, minIdx: int , maxIdx:int ) -> None:
        """callback: called when images are requested (occurs when page or zoom level is changed)."""

        imagesFilenames : list[str] = self.imagesManagement.getImagesFilesnames()

        for sIdx in range(minIdx, maxIdx+1):

            gIdx : int|None = self.selectionMap.selectedlIndexToGlobalIndex(sIdx) 

            if gIdx != None: self.imagesManagement.requestLoad(imagesFilenames[gIdx])
            else: self.mainWindow.setGalleryImage(sIdx, None)


    #### image loaded
    #### -----------------------------------------------------------------
    def CBimageLoaded(self: App, filename: str):
        """"callback: called when requested image is loaded (asynchronous loading)."""

        image : ndarray = self.imagesManagement.images[filename]
        imageIdx = self.selectionMap.imageNameToSelectedIndex(filename)         

        if imageIdx != None: self.mainWindow.setGalleryImage(imageIdx, image)
        
        # Save original image
        self.originalImages[filename] = Image(copy(image), ColorSpace.sRGB, isHdr=False, name=filename)
        self.originalImages[filename].setMetadata(self.imagesManagement.getProcesspipe(filename))

    #### image selected
    #### -----------------------------------------------------------------
    def CBimageSelected(self: App, index):

        
        self.selectedImageIdx = index # index in selection

        gIdx : int | None= self.selectionMap.selectedlIndexToGlobalIndex(index)# global index

        if (gIdx != None):

            image : ndarray = self.imagesManagement.getImage(self.imagesManagement.getImagesFilesnames()[gIdx])
            tags : Tags = self.imagesManagement.getImageTags(self.imagesManagement.getImagesFilesnames()[gIdx])
            exif : dict[str,str] = self.imagesManagement.getImageExif(self.imagesManagement.getImagesFilesnames()[gIdx])
            score : int = self.imagesManagement.getImageScore(self.imagesManagement.getImagesFilesnames()[gIdx])

            self.mainWindow.setEditorImage(image)

            # update image info
            imageFilename : str =  self.imagesManagement.getImagesFilesnames()[gIdx] 
            imagePath : str =  self.imagesManagement.imagePath 
            self.processPipe = self.buildProcessPipe()
            #### if debug : print(f'App.CBimageSelected({index}) > path:{imagePath}')
            self.metaImage = self.imagesManagement.getProcesspipe(imageFilename)
            self.originalMeta = self.imagesManagement.getProcesspipe(imageFilename)
            self.saveMeta = self.imagesManagement.getProcesspipe(imageFilename)

            # self.mainWindow.loadJsonChanged.emit(self.metaImage)
            if self.metaImage:
                self.mainWindow.editBlock.edit.lightEdit.light.contrast.changeValue(self.metaImage)
                self.mainWindow.editBlock.edit.lightEdit.light.exposure.changeValue(self.metaImage)

            self.disabledContent = [{'exposure': True},{'contrast': True},{'lightness': True},[{'0': True},{'1': True},{'2': True},{'3': True},{'4': True}]]


            self.mainWindow.setInfo(imageFilename, imagePath, *Jexif.toTuple(exif))

            self.mainWindow.setScore(score)

            # update tags info
            self.mainWindow.resetTags()
            if tags:
                self.mainWindow.setTagsImage(tags.toGUI())

    #### tag changed
    #### -----------------------------------------------------------------
    def CBtagChanged(self, key: tuple[str, str], value : bool) -> None:


        if self.selectedImageIdx != None:
            imageName : str|None = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if debug : print(f'\t\t imageName:{imageName}')
            if imageName != None : self.imagesManagement.updateImageTag(imageName, key[0], key[1], value)
    
    #### score changed
    #### -----------------------------------------------------------------
    def CBscoreChanged(self, value : int) -> None:


        if self.selectedImageIdx != None:
            imageName : str|None = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)

            if imageName != None : self.imagesManagement.updateImageScore(imageName, value)


    ### score selection changed
    ### ------------------------------------------------------------------
    def CBscoreSelectionChanged(self: App, listSelectedScore : list[bool]) -> None:
        """called when selection changed."""


        # get {'image name': score}
        imageScores : dict[str, int] = self.imagesManagement.imageScore
        # selected score
        selectedScores : list[int] = []
        for i, selected in enumerate(listSelectedScore) :  
            if selected : selectedScores.append(i)
        # send info to selectionMap
        self.selectionMap.selectByScore(imageScores, selectedScores)
        self.update()

    def getImageInstance(self, imageName: str) -> Image | None:
        """
        Get an Image instance from image name.
        
        Args:
            imageName (str, required)
        """
        img_data = self.imagesManagement.getImage(imageName)

        if isinstance(img_data, ndarray):
            img = Image(img_data, ColorSpace.sRGB, isHdr=False, name=imageName)
            img.setMetadata(self.metaImage)
            return img
        return None

    def updateImage(self, imageName: str, new_image: Image) -> None:
        """
        Update the image in ImageFiles and refresh the GUI.
        
        Args:
            imageName (str, required)
            new_image (Image, required)
        """
        imageIdx = self.selectionMap.imageNameToSelectedIndex(imageName)
        if imageIdx is not None:
            self.mainWindow.setGalleryImage(imageIdx, new_image.cData)
            if self.selectedImageIdx == imageIdx:
                self.mainWindow.setEditorImage(new_image.cData)
        self.metaImage = new_image.metadata
        self.originalImages[imageName].setMetadata(self.metaImage)
        self.imagesManagement.saveProcesspipe(imageName,self.metaImage)

    def applyProcessing(self, img: Image, processPipe: dict) -> Image:
        """
        Get an Image instance from image name.
        
        Args:
            imageName (str, required)
        """
        return coreC.coreCcompute(img, processPipe)

    def onExposureChanged(self, value: float):
        """
        Refresh the image when it receives the change signal from Exposure
        
        Args:
            value (float, required)
        """
        print(f'Exposure changed: {value}')
        if self.selectedImageIdx is not None:
            if self.disabledContent[0]['exposure'] is True:
                imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
                if self.processPipe:
                    img = self.getImageInstance(imageName)
                    self.processPipe.setImage(img)

                    self.processPipe.setParameters(0, {'EV': value})
                    
                    newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                    self.updateImage(imageName, newImage)

    def onContrastScalingChanged(self, value: float):
        """
        refresh the image when it receives the change signal
        
        Args:
            value (float, required)
        """
        print(f'Contrast scaling changed: {value}')
        if self.selectedImageIdx is not None:
            if self.disabledContent[1]['contrast'] is True:
                imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
                if self.processPipe:
                    img = self.getImageInstance(imageName)
                    self.processPipe.setImage(img)
                    self.processPipe.setParameters(1, {'contrast': value})

                    newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                    self.updateImage(imageName, newImage)
    
    def onLightnessRangeChanged(self, value: tuple):
        """
        Refresh the image when it receives the signal
        
        Args:
            value (tuple [min, max], required)
        """
        print(f'Highlights changed: {value}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                dico = self.processPipe.getParameters(2)
                dico['start'] = [value[0], value[0]]
                dico['end'] = [value[1], value[1]]
                self.processPipe.setParameters(2, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)
            
    def onHighlightsChanged(self, value: int):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal
        
        Args:
            value (int, required)
        """
        print(f'Highlights changed: {value}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                dico = self.processPipe.getParameters(2)
                dico['highlights'] = [value, value]
                self.processPipe.setParameters(2, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)

    def onShadowsChanged(self, value: float):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal
        
        Args:
            value (float, required)
        """
        print(f'Shadows changed: {value}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                dico = self.processPipe.getParameters(2)
                dico['shadows'] = [value, value]
                self.processPipe.setParameters(2, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)

    def onWhitesChanged(self, value: float):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal
        
        Args:
            value (float, required)
        """
        print(f'Whites changed: {value}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                dico = self.processPipe.getParameters(2)
                dico['whites'] = [value, value]
                self.processPipe.setParameters(2, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)

    def onBlacksChanged(self, value: float):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal
        
        Args:
            value (float, required)
        """
        print(f'Blacks changed: {value}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                dico = self.processPipe.getParameters(2)
                dico['blacks'] = [value, value]
                self.processPipe.setParameters(2, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)

    def onMediumsChanged(self, value: float):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal
        
        Args:
            value (float, required)
        """
        print(f'Mediums changed: {value}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                dico = self.processPipe.getParameters(2)
                dico['mediums'] = [value, value]
                self.processPipe.setParameters(2, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)







    def onHueShiftChanged(self, value: float, value2: int):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal d'un des Colors (0, 1, 2, 3, 4)
        
        Args:
            value (float, required)
            valuue2 (int, required)
        """
        print(f'Hue Shift changed: {value, value2}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                
                nb = value2+5
                dico = self.processPipe.getParameters(nb)
                dico['edit']['hue'] = value

                self.processPipe.setParameters(nb, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)

    def onSaturationChanged(self, value: float, value2: int):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal d'un des Colors (0, 1, 2, 3, 4)
        
        Args:
            value (float, required)
            valuue2 (int, required)
        """
        print(f'Saturation changed: {value, value2}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)

                nb = value2+5
                dico = self.processPipe.getParameters(nb)
                dico['edit']['saturation'] = value
                
                self.processPipe.setParameters(nb, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)

    def onColorExposureChanged(self, value: float, value2: int):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal d'un des Colors (0, 1, 2, 3, 4)
        
        Args:
            value (float, required)
            valuue2 (int, required)
        """
        print(f'Color exposure changed: {value, value2}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                
                nb = value2+5
                dico = self.processPipe.getParameters(nb)
                dico['edit']['exposure'] = value
                
                self.processPipe.setParameters(nb, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)

    def onColorContrastChanged(self, value: float, value2: int):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal d'un des Colors (0, 1, 2, 3, 4)
        
        Args:
            value (float, required)
            valuue2 (int, required)
        """
        print(f'Color contrast changed: {value, value2}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                
                nb = value2+5
                dico = self.processPipe.getParameters(nb)
                dico['edit']['contrast'] = value
                
                self.processPipe.setParameters(nb, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)

    def onHueRangeChanged(self, value: tuple, value2: int):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal d'un des Colors (0, 1, 2, 3, 4)
        
        Args:
            value (float, required)
            valuue2 (int, required)
        """
        print(f'Hue range changed: {value, value2}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                
                nb = value2+5
                dico = self.processPipe.getParameters(nb)
                dico['selection']['hue'] = value
                
                self.processPipe.setParameters(nb, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)
    def onChromaRangeChanged(self, value: tuple, value2: int):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal d'un des Colors (0, 1, 2, 3, 4)
        
        Args:
            value (float, required)
            valuue2 (int, required)
        """
        print(f'Chroma range changed: {value, value2}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                
                nb = value2+5
                dico = self.processPipe.getParameters(nb)
                dico['selection']['chroma'] = value
                
                self.processPipe.setParameters(nb, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)
    def onLightness2RangeChanged(self, value: tuple, value2: int):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal d'un des Colors (0, 1, 2, 3, 4)
        
        Args:
            value (float, required)
            valuue2 (int, required)
        """
        print(f'Lightness range changed: {value, value2}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)
                
                nb = value2+5
                dico = self.processPipe.getParameters(nb)
                dico['selection']['lightness'] = value
                
                self.processPipe.setParameters(nb, dico)

                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)

    def onActiveContrastChanged(self, value: bool):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal d'activation ou désactivation
        
        Args:
            value (bool, required)
        """
        print(f'Active contrast changed: {value}')
        if self.originalMeta is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.saveMeta is None:
                tempSave = self.imagesManagement.getProcesspipe(imageName)
                self.saveMeta[1]['contrast']['contrast'] = tempSave[1]['contrast']['contrast']
            
            img = self.getImageInstance(imageName)
            self.processPipe.setImage(img)
            if value == True:
                self.processPipe.setParameters(1, {'contrast': self.saveMeta[1]['contrast']['contrast']})
            if value == False:
                self.saveMeta[1]['contrast']['contrast'] = self.metaImage[1]['contrast']['contrast']
                self.processPipe.setParameters(1, {'contrast': self.originalMeta[1]['contrast']['contrast']})
                
            self.disabledContent[1]['contrast'] = value
            newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
            self.updateImage(imageName, newImage)

    def onActiveExposureChanged(self, value: bool):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal d'activation ou désactivation
        
        Args:
            value (bool, required)
        """
        print(f'Active exposure changed: {value}')
        if self.originalMeta is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.saveMeta is None:
                tempSave = self.imagesManagement.getProcesspipe(imageName)
                self.saveMeta[0]['exposure']['EV'] = tempSave[0]['exposure']['EV']
            
            img = self.getImageInstance(imageName)
            self.processPipe.setImage(img)
            if value == True:
                self.processPipe.setParameters(0, {'EV': self.saveMeta[0]['exposure']['EV']})
            if value == False:
                self.saveMeta[0]['exposure']['EV'] = self.metaImage[0]['exposure']['EV']
                self.processPipe.setParameters(0, {'EV': self.originalMeta[0]['exposure']['EV']})
                
            self.disabledContent[0]['exposure'] = value
            newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
            self.updateImage(imageName, newImage)
    
    def onActiveLightnessChanged(self, value: bool):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal d'activation ou désactivation
        
        Args:
            value (bool, required)
        """
        print(f'Active lightness changed: {value}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)

                if value == True:
                    self.processPipe.setParameters(2, self.saveMeta[2]['tonecurve'])
                if value == False:
                    self.saveMeta[2]['tonecurve'] = self.metaImage[2]['tonecurve']
                    self.processPipe.setParameters(2, self.originalMeta[2]['tonecurve'])

                self.disabledContent[2]['lightness'] = value
                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)
    
    def onActiveColorsChanged(self, value: bool, value2: int):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal d'activation ou désactivation d'un des colors (0, 1, 2, 3, 4)
        
        Args:
            value (bool, required)
            value2 (int, required)
        """
        print(f'Active colors changed: {value}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if self.processPipe:
                nb = value2+5

                if self.saveMeta is None:
                    tempSave = self.imagesManagement.getProcesspipe(imageName)
                    print(tempSave)
                    self.saveMeta[nb]['colorEditor'+str(value2)] = tempSave[nb]['colorEditor'+str(value2)]
                img = self.getImageInstance(imageName)
                self.processPipe.setImage(img)

                if value == True:
                    self.processPipe.setParameters(nb, self.saveMeta[nb]['colorEditor'+str(value2)])
                if value == False:
                    self.saveMeta[nb]['colorEditor'+str(value2)] = self.metaImage[nb]['colorEditor'+str(value2)]
                    self.processPipe.setParameters(nb, self.originalMeta[nb]['colorEditor'+str(value2)])

                self.disabledContent[3][value2+1] = value
 
                newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                self.updateImage(imageName, newImage)

    def onAutoClickedExposure(self, value: bool):
        """ xx
        Permet d'actualiser l'image quand il reçoit le signal du bouton "auto" quand il clique dans la section "Exposure"
        
        Args:
            value (bool, required)
        """
        if self.selectedImageIdx is not None:
            if self.disabledContent[0]['exposure'] is True:
                imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
                if self.processPipe:
                    img = self.getImageInstance(imageName)
                    self.processPipe.setImage(img)

                    self.processPipe.setParameters(0, {'EV': value})
                    
                    newImage = coreC.coreCcompute(self.processPipe.getImage(), self.processPipe.toDict())
                    self.updateImage(imageName, newImage)
        
    @staticmethod
    def buildProcessPipe():
        """
        WARNING: 
            here the process-pipe is built
            initial pipe does not have input image
            initial pipe has processes node according to EditImageView 
        """
        processPipe = processing.ProcessPipe()

        # exposure --------------------------------------------------------------------------------------------------------- 0
        defaultParameterEV = {'EV': 0}                                              
        idExposureProcessNode = processPipe.append(processing.exposure(), paramDict=None,name="exposure")   
        processPipe.setParameters(idExposureProcessNode, defaultParameterEV)                                        

        # contrast --------------------------------------------------------------------------------------------------------- 1
        defaultParameterContrast = {'contrast': 0}                                  
        idContrastProcessNode = processPipe.append(processing.contrast(), paramDict=None,  name="contrast") 
        processPipe.setParameters(idContrastProcessNode, defaultParameterContrast)                                  

        #tonecurve --------------------------------------------------------------------------------------------------------- 2
        defaultParameterYcurve = {'start':[0,0], 
                                  'shadows': [10,10],
                                  'blacks': [30,30], 
                                  'mediums': [50,50], 
                                  'whites': [70,70], 
                                  'highlights': [90,90], 
                                  'end': [100,100]}                         
        idYcurveProcessNode = processPipe.append(processing.Ycurve(), paramDict=None,name="tonecurve")      
        processPipe.setParameters(idYcurveProcessNode, defaultParameterYcurve)   
        
        # masklightness --------------------------------------------------------------------------------------------------------- 3
        defaultMask = { 'shadows': False, 
                       'blacks': False, 
                       'mediums': False, 
                       'whites': False, 
                       'highlights': False}
        idLightnessMaskProcessNode = processPipe.append(processing.lightnessMask(), paramDict=None, name="lightnessmask")  
        processPipe.setParameters(idLightnessMaskProcessNode, defaultMask)  

        # saturation --------------------------------------------------------------------------------------------------------- 4
        defaultValue = {'saturation': 0.0,  'method': 'gamma'}
        idSaturationProcessNode = processPipe.append(processing.saturation(), paramDict=None, name="saturation")    
        processPipe.setParameters(idSaturationProcessNode, defaultValue)                     

        # colorEditor0 --------------------------------------------------------------------------------------------------------- 5
        defaultParameterColorEditor0= {'selection': {'lightness': (0,100),'chroma': (0,100),'hue':(0,360)},  
                                       'edit': {'hue': 0.0, 'exposure':0.0, 'contrast':0.0,'saturation':0.0}, 
                                       'mask': False}        
        idColorEditor0ProcessNode = processPipe.append(processing.colorEditor(), paramDict=None, name="colorEditor0")  
        processPipe.setParameters(idColorEditor0ProcessNode, defaultParameterColorEditor0)

        # colorEditor1 --------------------------------------------------------------------------------------------------------- 6
        defaultParameterColorEditor1= {'selection': {'lightness': (0,100),'chroma': (0,100),'hue':(0,360)},  
                                       'edit': {'hue': 0.0, 'exposure':0.0, 'contrast':0.0,'saturation':0.0}, 
                                       'mask': False}        
        idColorEditor1ProcessNode = processPipe.append(processing.colorEditor(), paramDict=None, name="colorEditor1")  
        processPipe.setParameters(idColorEditor1ProcessNode, defaultParameterColorEditor1)
        
        # colorEditor2 --------------------------------------------------------------------------------------------------------- 7
        defaultParameterColorEditor2= {'selection': {'lightness': (0,100),'chroma': (0,100),'hue':(0,360)},  
                                       'edit': {'hue': 0.0, 'exposure':0.0, 'contrast':0.0,'saturation':0.0}, 
                                       'mask': False}        
        idColorEditor2ProcessNode = processPipe.append(processing.colorEditor(), paramDict=None, name="colorEditor2")  
        processPipe.setParameters(idColorEditor2ProcessNode, defaultParameterColorEditor2)
        
        # colorEditor3 --------------------------------------------------------------------------------------------------------- 8
        defaultParameterColorEditor3= {'selection': {'lightness': (0,100),'chroma': (0,100),'hue':(0,360)},  
                                       'edit': {'hue': 0.0, 'exposure':0.0, 'contrast':0.0,'saturation':0.0}, 
                                       'mask': False}        
        idColorEditor3ProcessNode = processPipe.append(processing.colorEditor(), paramDict=None, name="colorEditor3")  
        processPipe.setParameters(idColorEditor3ProcessNode, defaultParameterColorEditor3)
        
        # colorEditor4 --------------------------------------------------------------------------------------------------------- 9
        defaultParameterColorEditor4= {'selection': {'lightness': (0,100),'chroma': (0,100),'hue':(0,360)},  
                                       'edit': {'hue': 0.0, 'exposure':0.0, 'contrast':0.0,'saturation':0.0}, 
                                       'mask': False}        
        idColorEditor4ProcessNode = processPipe.append(processing.colorEditor(), paramDict=None, name="colorEditor4")  
        processPipe.setParameters(idColorEditor4ProcessNode, defaultParameterColorEditor4)

        # geometry --------------------------------------------------------------------------------------------------------- 10
        defaultValue = { 'ratio': (16,9), 'up': 0,'rotation': 0.0}
        idGeometryNode = processPipe.append(processing.geometry(), paramDict=None, name="geometry")    
        processPipe.setParameters(idGeometryNode, defaultValue)
        # ------------ --------------------------------------------------------------------------------------------------------- 

        return processPipe