# ImageFiles.py
from __future__ import annotations
import os
from core.image import Image, filenamesplit
from numpy import ndarray

from PyQt6.QtCore import QObject, pyqtSignal, QThreadPool, QRunnable
from app.Jexif import Jexif
from app.Tags import Tags
from app.Score import Score
from preferences.Prefs import Prefs

debug: bool = True

class ImageFiles(QObject):
    """Manages image files in the directory: asynchronous loading, caching images."""
    imageLoaded: pyqtSignal = pyqtSignal(str)

    def __init__(self: ImageFiles) -> None: 
        super().__init__()
        self.imagePath: str = '.'
        self.extraPath: str = '.uHDR'
        self.nbImages: int = 0
        self.imageFilenames: list[str] = []
        self.imageIsLoaded: dict[str, bool] = {}
        self.imageIsThumbnail: dict[str, bool] = {}
        self.images: dict[str, ndarray] = {}
        self.imageScore: dict[str, int] = {}
        self.imageTags: dict[str, Tags] = {}
        self.imageExif: dict[str, dict[str, str]] = {}
        self.pool = QThreadPool.globalInstance()

    def reset(self: ImageFiles):
        self.imageFilenames = []
        self.imageIsLoaded = {}
        self.imageIsThumbnail = {}
        self.images = {}
        self.imageScore = {}
        self.imageTags = {}
        self.imageExif = {}

    def __repr__(self: ImageFiles) -> str:
        res = '-------------------  imageFiles -------------------------------'
        res += f'\n image path: {self.imagePath}'
        res += f'\n extra path: {self.extraPath}'
        res += f'\n nb images: {self.nbImages}'
        res += f'\n filenames: {self.imageFilenames}'
        res += f'\n images: '
        for file in self.imageFilenames:
            res += f'\n\t "{file}" > loaded: {self.imageIsLoaded[file]}'
            res += f'\n\t "{file}" > exif: {self.imageExif[file] if file in self.imageExif.keys() else "not loaded"}' 
            res += f'\n\t "{file}" > score: {self.imageScore[file] if file in self.imageExif.keys() else "not loaded"}' 
            res += f'\n\t "{file}" > tags: {self.imageTags[file] if file in self.imageTags.keys() else "not loaded"}' 
        res += '\n-------------------  imageFiles End ----------------------------'
        return res

    def getNbImages(self: ImageFiles) -> int: 
        """Return the number of image files."""
        return len(self.imageFilenames)

    def getImagesFilesnames(self: ImageFiles) -> list[str]: 
        """Return the list of image files."""
        return self.imageFilenames

    def setPrefs(self: ImageFiles) -> None:
        """Update attributes according to preferences."""
        self.imagePath = Prefs.currentDir
        self.extraPath = Prefs.extraPath

    def setDirectory(self: ImageFiles, dirPath: str) -> int:
        """Set directory: scan for image files."""
        if debug: print(f'ImageFiles.setDirectory({dirPath})')

        self.reset()
        self.imagePath = dirPath
        ext: tuple[str] = tuple(Prefs.imgExt)
        filenames = sorted(os.listdir(dirPath))
        self.imageFilenames = list(filter(lambda x: x.endswith(ext), filenames))
        self.nbImages = len(self.imageFilenames)

        for filename in self.imageFilenames:
            self.imageIsLoaded[filename] = False

        self.checkExtra()

        for filename in self.imageFilenames:
            self.imageTags[filename] = Tags.load(self.imagePath, filename, self.extraPath)
            self.imageExif[filename] = Jexif.load(self.imagePath, filename, self.extraPath)
            self.imageScore[filename] = Score.load(self.imagePath, filename, self.extraPath)

        return len(self.imageFilenames)

    def requestLoad(self: ImageFiles, filename: str, thumbnail: bool = True):
        """Add an image loading request to pool thread."""
        if debug: print(f'ImageFiles.requestLoad({filename}, thumbnail={thumbnail})')

        if not self.imageIsLoaded[filename]:
            self.imageTags[filename] = Tags.load(self.imagePath, filename, self.extraPath)
            self.imageExif[filename] = Jexif.load(self.imagePath, filename, self.extraPath)
            self.imageScore[filename] = Score.load(self.imagePath, filename, self.extraPath)

            filename_ = os.path.join(self.imagePath, filename)
            self.pool.start(RunLoadImage(self, filename_, thumbnail))
        else:
            self.imageLoaded.emit(filename)

    def endLoadImage(self: ImageFiles, error: bool, filename: str):
        """Called when an image is loaded."""
        if debug: print(f'ImageFiles.endLoadImage( error={error}, {filename})')

        if not error:
            filename = filename.split('\\')[-1]
            self.imageIsLoaded[filename] = True 
            self.imageLoaded.emit(filename)
        else:
            self.requestLoad(filename)  

    def getImage(self: ImageFiles, name: str, thumbnail: bool = True) -> ndarray:
        """Get image, assumption image is loaded."""
        image = self.images.get(name)
        if image is None:
            print(f"Image not found for name: {name}")
            return np.zeros((0, 0, 3))
        return image

    def getImageTags(self: ImageFiles, name: str) -> Tags: 
        return self.imageTags[name]

    def getImageExif(self: ImageFiles, name: str) -> dict[str, str]: 
        return self.imageExif[name]

    def getImageScore(self: ImageFiles, name: str) -> int: 
        return self.imageScore[name]

    def checkExtra(self: ImageFiles) -> None:
        ePath: str = os.path.join(self.imagePath, self.extraPath) 
        if not os.path.exists(ePath):
            os.mkdir(ePath)

    def updateImageTag(self: ImageFiles, imageName: str, type: str, name: str, value: bool) -> None:
        self.imageTags[imageName].add(type, name, value)
        self.imageTags[imageName].save(self.imagePath, self.extraPath, imageName)

    def updateImageScore(self: ImageFiles, imageName: str, value: int) -> None:
        self.imageScore[imageName] = value
        Score.save(self.imagePath, self.extraPath, imageName, self.imageScore[imageName])

class RunLoadImage(QRunnable):
    def __init__(self: RunLoadImage, parent: ImageFiles, filename: str, thumbnail: bool = True):
        super().__init__()
        self.parent: ImageFiles = parent
        self.filename: str = filename
        self.thumbnail: bool = thumbnail

    def run(self: RunLoadImage):
        if debug: print(f'RunLoadImage.run({self.filename})')

        try:
            if os.path.exists(self.filename):
                if self.thumbnail: 
                    path, name, ext = filenamesplit(self.filename)
                    thumbnailName: str = os.path.join(path, Prefs.extraPath, Prefs.thumbnailPrefix + name + '.' + ext)
                    
                    if os.path.exists(thumbnailName):
                        imageSmall: Image = Image.read(thumbnailName)
                    else:
                        imageBig: Image = Image.read(self.filename)
                        imageSmall: Image = imageBig.buildThumbnail(Prefs.thumbnailMaxSize)
                        imageSmall.write(thumbnailName)
                    
                    self.parent.images[self.filename.split('\\')[-1]] = imageSmall.cData 
                else:
                    imageBig = Image.read(self.filename)
                    self.parent.images[self.filename.split('\\')[-1]] = imageBig.cData 
                
                # Debug: Verify if the image is correctly stored
                if self.filename.split('\\')[-1] in self.parent.images:
                    print(f"Image stored with key: {self.filename.split('\\')[-1]}")
                else:
                    print(f"Failed to store image with key: {self.filename.split('\\')[-1]}")
            
            self.parent.endLoadImage(False, self.filename)
        except(IOError, ValueError) as e:
            self.parent.endLoadImage(True, self.filename)
