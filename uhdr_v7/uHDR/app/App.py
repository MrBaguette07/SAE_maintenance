from __future__ import annotations
from numpy import ndarray
from app.Jexif import Jexif
import preferences.Prefs
from guiQt.MainWindow import MainWindow
from app.ImageFIles import ImageFiles
from app.Tags import Tags
from app.SelectionMap import SelectionMap
from hdrCore import processing, coreC, utils
from core.image import Image  # Assurez-vous d'importer la classe Image appropriée
from core.colourSpace import ColorSpace  # Import ColorSpace as well

debug: bool = True

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
        self.mainWindow.contrastOffsetChanged.connect(self.onContrastOffsetChanged)
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

        self.mainWindow.setPrefs()

    # methods
    # -----------------------------------------------------------------

    ##  getImageRangeIndex
    def getImageRangeIndex(self: App) -> tuple[int, int]: 
        """Return the index range (min index, max index) of images displayed by the gallery."""
        return self.mainWindow.imageGallery.getImageRangeIndex()

    ##  update
    def update(self: App) -> None:
        """Call to update gallery after selection changed or directory changed."""
        minIdx, maxIdx = self.getImageRangeIndex()
        self.mainWindow.setNumberImages(self.selectionMap.getSelectedImageNumber())
        self.mainWindow.setNumberImages(maxIdx - minIdx)
        self.CBrequestImages(minIdx, maxIdx)

    ## app logic: callbacks 
    #### select new directory
    def CBdirSelected(self: App, path: str) -> None:
        """Callback: called when directory is selected."""
        if debug: print(f'App.CBdirSelected({path})')
        self.imagesManagement.setDirectory(path)
        self.selectionMap.setImageNames(self.imagesManagement.getImagesFilesnames())
        self.selectionMap.selectAll()
        self.mainWindow.resetGallery()
        self.mainWindow.setNumberImages(self.imagesManagement.getNbImages())
        self.mainWindow.firstPage()

    #### request image: zoom or page changed
    def CBrequestImages(self: App, minIdx: int, maxIdx: int) -> None:
        """Callback: called when images are requested (occurs when page or zoom level is changed)."""
        imagesFilenames: list[str] = self.imagesManagement.getImagesFilesnames()
        for sIdx in range(minIdx, maxIdx + 1):
            gIdx: int | None = self.selectionMap.selectedlIndexToGlobalIndex(sIdx)
            if gIdx is not None:
                self.imagesManagement.requestLoad(imagesFilenames[gIdx])
            else:
                self.mainWindow.setGalleryImage(sIdx, None)

    #### image loaded
    def CBimageLoaded(self: App, filename: str) -> None:
        """Callback: called when requested image is loaded (asynchronous loading)."""
        image: ndarray = self.imagesManagement.images[filename]
        imageIdx = self.selectionMap.imageNameToSelectedIndex(filename)
        if imageIdx is not None:
            self.mainWindow.setGalleryImage(imageIdx, image)

    #### image selected
    def CBimageSelected(self: App, index) -> None:
        self.selectedImageIdx = index
        gIdx: int | None = self.selectionMap.selectedlIndexToGlobalIndex(index)
        if gIdx is not None:
            image: ndarray = self.imagesManagement.getImage(self.imagesManagement.getImagesFilesnames()[gIdx])
            tags: Tags = self.imagesManagement.getImageTags(self.imagesManagement.getImagesFilesnames()[gIdx])
            exif: dict[str, str] = self.imagesManagement.getImageExif(self.imagesManagement.getImagesFilesnames()[gIdx])
            score: int = self.imagesManagement.getImageScore(self.imagesManagement.getImagesFilesnames()[gIdx])
            self.mainWindow.setEditorImage(image)
            imageFilename: str = self.imagesManagement.getImagesFilesnames()[gIdx]
            imagePath: str = self.imagesManagement.imagePath
            self.mainWindow.setInfo(imageFilename, imagePath, *Jexif.toTuple(exif))
            self.mainWindow.setScore(score)
            self.mainWindow.resetTags()
            if tags:
                self.mainWindow.setTagsImage(tags.toGUI())

    #### tag changed
    def CBtagChanged(self: App, key: tuple[str, str], value: bool) -> None:
        if self.selectedImageIdx is not None:
            imageName: str | None = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if imageName is not None:
                self.imagesManagement.updateImageTag(imageName, key[0], key[1], value)

    #### score changed
    def CBscoreChanged(self: App, value: int) -> None:
        if self.selectedImageIdx is not None:
            imageName: str | None = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            if imageName is not None:
                self.imagesManagement.updateImageScore(imageName, value)

    ### score selection changed
    def CBscoreSelectionChanged(self: App, listSelectedScore: list[bool]) -> None:
        """Called when selection changed."""
        imageScores: dict[str, int] = self.imagesManagement.imageScore
        selectedScores: list[int] = [i for i, selected in enumerate(listSelectedScore) if selected]
        self.selectionMap.selectByScore(imageScores, selectedScores)
        self.update()

    # Functions from processing.py
    def getImageInstance(self, imageName: str) -> Image | None:
        """Get an Image instance from image name."""
        img_data = self.imagesManagement.getImage(imageName)
        if isinstance(img_data, ndarray):
            # Suppose the color space is sRGB and the image is not HDR by default
            img = Image(img_data, ColorSpace.sRGB, isHdr=False)
            return img
        return None

    def onExposureChanged(self, value: float):
        print(f'Exposure changed: {value}')
        # Utiliser la classe 'exposure' de processing
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                exposure = processing.exposure()
                new_image = exposure.compute(img, EV=value)
                self.imagesManagement.updateImage(imageName, new_image)

    def onContrastScalingChanged(self, value: float):
        print(f'Contrast scaling changed: {value}')
        # Utiliser la classe 'contrast' de processing
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                contrast = processing.contrast()
                new_image = contrast.compute(img, contrast=value)
                self.imagesManagement.updateImage(imageName, new_image)


    def onContrastOffsetChanged(self, value: float):
        print(f'Contrast offset changed: {value}')
        # Utiliser la classe 'contrast' de processing avec un offset
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                contrast = processing.contrast()
                new_image = contrast.compute(img, contrast=value)
                self.imagesManagement.updateImage(imageName, new_image)

    def onLightnessRangeChanged(self, value: tuple):
        print(f'Lightness range changed: {value}')
        # Utiliser la classe 'lightnessMask' de processing
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                lightness_mask = processing.lightnessMask()
                new_image = lightness_mask.compute(img, lightness_range=value)
                self.imagesManagement.updateImage(imageName, new_image)

    def onHueShiftChanged(self, value: float):
        print(f'Hue Shift changed: {value}')
        # Utiliser la classe 'colorEditor' de processing
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                color_editor = processing.colorEditor()
                new_image = color_editor.compute(img, edit={'hue': value})
                self.imagesManagement.updateImage(imageName, new_image)

    def onSaturationChanged(self, value: float):
        print(f'Saturation changed: {value}')
        # Utiliser la classe 'saturation' de processing
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                saturation = processing.saturation()
                new_image = saturation.compute(img, saturation=value)
                self.imagesManagement.updateImage(imageName, new_image)

    def onColorExposureChanged(self, value: float):
        print(f'Color exposure changed: {value}')
        # Utiliser la classe 'colorEditor' de processing pour modifier l'exposition des couleurs
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                color_editor = processing.colorEditor()
                new_image = color_editor.compute(img, edit={'exposure': value})
                self.imagesManagement.updateImage(imageName, new_image)

    def onColorContrastChanged(self, value: float):
        print(f'Color contrast changed: {value}')
        # Utiliser la classe 'colorEditor' de processing pour modifier le contraste des couleurs
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                color_editor = processing.colorEditor()
                new_image = color_editor.compute(img, edit={'contrast': value})
                self.imagesManagement.updateImage(imageName, new_image)

    def onHighlightsChanged(self, value: float):
        print(f'Highlights changed: {value}')
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                ycurve = processing.Ycurve()
                new_image = ycurve.compute(img, highlights=value)
                self.imagesManagement.updateImage(imageName, new_image)


    def onShadowsChanged(self, value: float):
        print(f'Shadows changed: {value}')
        # Utiliser la classe 'Ycurve' de processing pour modifier les ombres
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                ycurve = processing.Ycurve()
                new_image = ycurve.compute(img, shadows=value)
                self.imagesManagement.updateImage(imageName, new_image)

    def onWhitesChanged(self, value: float):
        print(f'Whites changed: {value}')
        # Utiliser la classe 'Ycurve' de processing pour modifier les blancs
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                ycurve = processing.Ycurve()
                new_image = ycurve.compute(img, whites=value)
                self.imagesManagement.updateImage(imageName, new_image)

    def onBlacksChanged(self, value: float):
        print(f'Blacks changed: {value}')
        # Utiliser la classe 'Ycurve' de processing pour modifier les noirs
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                ycurve = processing.Ycurve()
                new_image = ycurve.compute(img, blacks=value)
                self.imagesManagement.updateImage(imageName, new_image)
    
    def onMediumsChanged(self, value: float):
        print(f'Mediums changed: {value}')
        # Utiliser la classe 'Ycurve' de processing pour modifier les tons moyens
        if self.selectedImageIdx is not None:
            imageName = self.selectionMap.selectedIndexToImageName(self.selectedImageIdx)
            img = self.getImageInstance(imageName)
            if img:
                ycurve = processing.Ycurve()
                new_image = ycurve.compute(img, mediums=value)
                self.imagesManagement.updateImage(imageName, new_image)
