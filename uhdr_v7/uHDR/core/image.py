# image.py
from __future__ import annotations
from core.colourSpace import ColorSpace
from copy import deepcopy
import numpy as np
import os
import colour
import skimage.transform
import matplotlib

debug: bool = True

def filenamesplit(filename):
    """Retrieve path, name, and extension from a filename."""
    path, nameWithExt = os.path.split(filename)
    splits = nameWithExt.split('.')
    ext = splits[-1].lower()
    name = ''.join(splits[:-1])
    return (path, name, ext)

class Image:
    """Color data + color space + HDR"""
    
    def __init__(self: Image, data: np.ndarray, space: ColorSpace = ColorSpace.sRGB, isHdr: bool = False):
        self.cSpace: ColorSpace = space
        self.cData: np.ndarray = data
        self.hdr: bool = isHdr
        print(f"Image initialized with data shape: {data}, min: {data.min()}, max: {data.max()}")
    
    def __repr__(self: Image) -> str:
        y, x, c = self.cData.shape
        res: str = '-------------------    Image   -------------------------------'
        res += f'\n size: {x} x {y} x {c} '
        res += f'\n colourspace: {self.cSpace.name}'
        res += f'\n hdr: {self.hdr}'
        res += f'\n Shape: {self.cData}'
        res += '\n-------------------  Image End -------------------------------'
        return res

    def write(self: Image, fileName: str):
        """Write image to system."""
        if self.hdr:
            max_val = np.max(self.cData)
            normalized_data = self.cData / max_val if max_val > 1 else self.cData
            colour.write_image((normalized_data * 255.0).astype(np.uint8), fileName, bit_depth='float32', method='Imageio')
        else:
            colour.write_image((self.cData * 255.0).astype(np.uint8), fileName, bit_depth='uint8', method='Imageio')
        print(f"Image written to {fileName} with min/max values: {np.min(self.cData)}, {np.max(self.cData)}")

    def buildThumbnail(self: Image, maxSize: int = 800) -> Image:
        """Build a thumbnail image."""
        y, x, _ = self.cData.shape
        factor: int = maxSize / max(y, x)
        print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
        if factor < 1:
            thumbcData = skimage.transform.resize(self.cData, (int(y * factor), int(x * factor)))
            return Image(thumbcData, self.cSpace, self.hdr)
        else:
            return deepcopy(self)

    @staticmethod
    def read(fileName: str) -> Image:
        """Read image from system."""
        img: Image
        path, name, ext = filenamesplit(fileName)
        if os.path.exists(fileName):
            if ext in ["jpg", "jpeg", "png"]:
                imgData: np.ndarray = colour.read_image(fileName, bit_depth='float32', method='Imageio')
                img = Image(imgData, ColorSpace.sRGB, False)
            elif ext == "hdr":
                imgData: np.ndarray = colour.read_image(fileName, bit_depth='float32', method='Imageio')
                img = Image(imgData, ColorSpace.sRGB, True)
            else:
                raise ValueError(f"Unsupported image format: {ext}")
            print(f"Image read from {fileName} with shape: {imgData.shape}")
        else:
            img = Image(np.ones((600, 800, 3)) * 0.50, ColorSpace.sRGB, False)
            print(f"Default image created as {fileName} does not exist")
        return img

    # Méthodes d'ajustement
    def adjustExposure(self, value: float):
        self.cData = np.clip(self.cData * (1 + value), 0, 1)
        print(f"Exposure adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustContrastScaling(self, value: float):
        factor = (259 * (value + 255)) / (255 * (259 - value))
        self.cData = np.clip(factor * (self.cData - 0.5) + 0.5, 0, 1)
        print(f"Contrast scaling adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustContrastOffset(self, value: float):
        self.cData = np.clip(self.cData + value, 0, 1)
        print(f"Contrast offset adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustLightnessRange(self, value: tuple):
        min_light, max_light = value
        self.cData = np.clip((self.cData - min_light) / (max_light - min_light), 0, 1)
        # print(self.cData, "àààààààààààààààààààààààààààààààààààààààààààààààààààààààààààààààààààààààààààà")
        print(f"Lightness range adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustHueShift(self, value: float):
        hsv = self.rgb_to_hsv(self.cData)
        hsv[..., 0] = (hsv[..., 0] + value) % 1.0
        self.cData = self.hsv_to_rgb(hsv)
        print(f"Hue shift adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustSaturation(self, value: float):
        hsv = self.rgb_to_hsv(self.cData)
        hsv[..., 1] = np.clip(hsv[..., 1] * (1 + value), 0, 1)
        self.cData = self.hsv_to_rgb(hsv)
        print(f"Saturation adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustColorExposure(self, value: float):
        self.cData = np.clip(self.cData * (1 + value), 0, 1)
        print(f"Color exposure adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustColorContrast(self, value: float):
        factor = (259 * (value + 255)) / (255 * (259 - value))
        self.cData = np.clip(factor * (self.cData - 0.5) + 0.5, 0, 1)
        print(f"Color contrast adjusted: min {self.cData.min()}, max {self.cData.max()}")

    @staticmethod
    def rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
        """Convert RGB to HSV"""
        print("jjjjjjjjjjjjjjjjjj")
        return matplotlib.colors.rgb_to_hsv(rgb)

    @staticmethod
    def hsv_to_rgb(hsv: np.ndarray) -> np.ndarray:
        """Convert HSV to RGB"""
        print("dddddddddddddddddddddddddddd")
        return matplotlib.colors.hsv_to_rgb(hsv)
