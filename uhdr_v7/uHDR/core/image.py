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

# image.py
from __future__ import annotations
from core.colourSpace import ColorSpace
from copy import deepcopy
import numpy as np, os, colour
import skimage.transform
import matplotlib

debug: bool = True

def filenamesplit(filename):
    """retrieve path, name and extension from a filename."""
    path, nameWithExt = os.path.split(filename)
    splits = nameWithExt.split('.')
    ext = splits[-1].lower()
    name = ''.join(splits[:-1])
    return (path, name, ext)

class Image:
    """color data  +  color space + hdr"""
    
    def __init__(self: Image, data: np.ndarray, space: ColorSpace = ColorSpace.sRGB, isHdr: bool = False):
        self.cSpace: ColorSpace = space
        self.cData: np.ndarray = data
        self.hdr: bool = isHdr
    
    def __repr__(self: Image) -> str:
        y, x, c = self.cData.shape
        res: str = '-------------------    Image   -------------------------------'
        res += f'\n size: {x} x {y} x {c} '
        res += f'\n colourspace: {self.cSpace.name}'
        res += f'\n hdr: {self.hdr}'
        res += '\n-------------------  Image End -------------------------------'
        return res

    def write(self: Image, fileName: str):
        """write image to system."""
        if self.hdr:
            max_val = np.max(self.cData)
            normalized_data = self.cData / max_val if max_val > 1 else self.cData
            colour.write_image((normalized_data * 255.0).astype(np.uint8), fileName, bit_depth='float32', method='Imageio')
        else:
            colour.write_image((self.cData * 255.0).astype(np.uint8), fileName, bit_depth='uint8', method='Imageio')
        print(f"Image written to {fileName} with min/max values: {np.min(self.cData)}, {np.max(self.cData)}")

    def buildThumbnail(self: Image, maxSize: int = 800) -> Image:
        """build a thumbnail image."""
        y, x, _ = self.cData.shape
        factor: int = maxSize / max(y, x)
        if factor < 1:
            thumbcData = skimage.transform.resize(self.cData, (int(y * factor), int(x * factor)))
            return Image(thumbcData, self.cSpace, self.hdr)
        else:
            return deepcopy(self)

    @staticmethod
    def read(fileName: str) -> Image:
        """read image from system."""
        img: Image
        path, name, ext = filenamesplit(fileName)
        if os.path.exists(fileName):
            if ext == "jpg":
                imgData: np.ndarray = colour.read_image(fileName, bit_depth='float32', method='Imageio')
                img = Image(imgData, ColorSpace.sRGB, False)
            if ext == "hdr":
                imgData: np.ndarray = colour.read_image(fileName, bit_depth='float32', method='Imageio')
                img = Image(imgData, ColorSpace.sRGB, True)
        else:
            img = Image(np.ones((600, 800, 3)) * 0.50, ColorSpace.sRGB, False)
        return img

    # Méthodes d'ajustement
    def adjustExposure(self, value: float):
        self.cData = np.clip(self.cData * (1 + value), 0, 1)

    def adjustContrastScaling(self, value: float):
        factor = (259 * (value + 255)) / (255 * (259 - value))
        self.cData = np.clip(factor * (self.cData - 0.5) + 0.5, 0, 1)

    def adjustContrastOffset(self, value: float):
        self.cData = np.clip(self.cData + value, 0, 1)

    def adjustLightnessRange(self, value: tuple):
        min_light, max_light = value
        self.cData = np.clip((self.cData - min_light) / (max_light - min_light), 0, 1)

    def adjustHueShift(self, value: float):
        hsv = self.rgb_to_hsv(self.cData)
        hsv[..., 0] = (hsv[..., 0] + value) % 1.0
        self.cData = self.hsv_to_rgb(hsv)

    def adjustSaturation(self, value: float):
        hsv = self.rgb_to_hsv(self.cData)
        hsv[..., 1] = np.clip(hsv[..., 1] * (1 + value), 0, 1)
        self.cData = self.hsv_to_rgb(hsv)

    def adjustColorExposure(self, value: float):
        self.cData = np.clip(self.cData * (1 + value), 0, 1)

    def adjustColorContrast(self, value: float):
        factor = (259 * (value + 255)) / (255 * (259 - value))
        self.cData = np.clip(factor * (self.cData - 0.5) + 0.5, 0, 1)

    @staticmethod
    def rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
        # Conversion RGB vers HSV
        return matplotlib.colors.rgb_to_hsv(rgb)

    @staticmethod
    def hsv_to_rgb(hsv: np.ndarray) -> np.ndarray:
        # Conversion HSV vers RGB
        return matplotlib.colors.hsv_to_rgb(hsv)
