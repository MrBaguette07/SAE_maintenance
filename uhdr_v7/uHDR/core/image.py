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

from core.colourSpace import ColorSpace
from copy import deepcopy
import numpy as np, os, colour
import skimage.transform

# ------------------------------------------------------------------------------------------

debug: bool = True

# -----------------------------------------------------------------------------
def filenamesplit(filename):
    """retrieve path, name and extension from a filename.

    @Args:
        filename (str,Required): filename
            
    @Returns:
        (str,str,str): (path,name,ext)
            
    @Example:
        filenamesplit("./dir0/dir1/name.ext") returns ("./dir0/dir1/","name","ext")
    """
    
    path, nameWithExt = os.path.split(filename)
    splits = nameWithExt.split('.')
    ext = splits[-1].lower()
    name = '.'.join(splits[:-1])
    return (path, name, ext)

# ------------------------------------------------------------------------------------------
def adjust_brightness(image_data: np.ndarray, factor: float) -> np.ndarray:
    """
    Adjust the brightness of the image.
    
    Args:
        image_data (np.ndarray): Image data.
        factor (float): Factor to adjust brightness. >1 to increase brightness, <1 to decrease.
        
    Returns:
        np.ndarray: Brightness adjusted image.
    """
    return np.clip(image_data * factor, 0, 1)

# --- class Image -------------------------------------------------------------------------
class Image:
    """color data  +  color space + hdr"""
    # constructor
    # -----------------------------------------------------------------
    def __init__(self: Image, data: np.ndarray, space: ColorSpace = ColorSpace.sRGB, isHdr: bool = False):
        self.cSpace: ColorSpace = space
        self.cData: np.ndarray = data
        self.hdr: bool = isHdr
    
    # methods
    # -----------------------------------------------------------------
    def __repr__(self: Image) -> str:
        y, x, c = self.cData.shape
        res: str = '-------------------    Image   -------------------------------'
        res += f'\n size: {x} x {y} x {c} '
        res += f'\n colourspace: {self.cSpace.name}'
        res += f'\n hdr: {self.hdr}'
        res += '\n-------------------  Image End -------------------------------'
        return res
    
    # -----------------------------------------------------------------
    def write(self: Image, fileName: str, brightness_factor: float = 1.5):
        """write image to system."""
        if self.hdr:
            adjusted_data = adjust_brightness(self.cData, brightness_factor)
            gamma_corrected_data = np.clip(adjusted_data ** (1/2.2), 0, 1)
            
            colour.write_image(gamma_corrected_data, fileName, bit_depth='float32', method='Imageio')
        else:
            colour.write_image((self.cData * 255.0).astype(np.uint8), fileName, bit_depth='uint8', method='Imageio')

    # -----------------------------------------------------------------
    def buildThumbnail(self: Image, maxSize: int = 800) -> Image:
        """build a thumbnail image."""
        y, x, _ = self.cData.shape
        factor: int = maxSize / max(y, x)
        if factor < 1:
            thumbcData = skimage.transform.resize(self.cData, (int(y * factor), int(x * factor)))
            return Image(thumbcData, self.cSpace, self.hdr)
        else:
            return deepcopy(self)

    # static methods
    # -----------------------------------------------------------------
    @staticmethod
    def read(fileName: str) -> Image:
        """read image from system."""
        path, name, ext = filenamesplit(fileName)
        if os.path.exists(fileName):
            if ext in ["exr", "hdr"]:
                imgData = colour.io.read_image(fileName, bit_depth='float32', method='Imageio')

                adjusted_data = adjust_brightness(imgData, 1.5)
                gamma_corrected_data = np.clip(adjusted_data ** (1/2.2), 0, 1)

                return Image(gamma_corrected_data, ColorSpace.scRGB, True)
            else:
                imgData = colour.read_image(fileName, bit_depth='float32', method='Imageio')
                return Image(imgData, ColorSpace.sRGB, False)
        else:
            return Image(np.zeros((600, 800, 3)), ColorSpace.sRGB, False)
