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

debug : bool = True

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
    return (path,name,ext)


# ------------------------------------------------------------------------------------------
# --- class ImmageFiles(QObject) -----------------------------------------------------------
# ------------------------------------------------------------------------------------------
class Image:
    """color data  +  color space + hdr"""
    # constructor
    # -----------------------------------------------------------------
    def __init__(self:Image, data: np.ndarray, space: ColorSpace = ColorSpace.sRGB, isHdr: bool = False):

        self.cSpace : ColorSpace = space
        self.cData : np.ndarray = data
        self.hdr : bool = isHdr
    
    # methods
    # -----------------------------------------------------------------
    def __repr__(self: Image) -> str:
        y, x, c =  self.cData.shape
        res : str =  '-------------------    Image   -------------------------------'
        res += f'\n size: {x} x {y} x {c} '
        res += f'\n colourspace: {self.cSpace.name}'
        res += f'\n hdr: {self.hdr}'
        res +=  '\n-------------------  Image End -------------------------------'
        return res
    # -----------------------------------------------------------------
    def write(self: Image, fileName: str):
        """write image to system."""
        
        # Normalizing HDR images if needed
        if self.hdr:
            max_val = np.max(self.cData)
            normalized_data = self.cData / max_val if max_val > 1 else self.cData
            colour.write_image((normalized_data * 255.0).astype(np.uint8), fileName, bit_depth='float32', method='Imageio')
        else:
            colour.write_image((self.cData * 255.0).astype(np.uint8), fileName, bit_depth='uint8', method='Imageio')



#           elif ext =="hdr":
#             if thumb: 
#                 # do not read input only the thumbnail
#                 searchStr = os.path.join(path,"thumbnails","_"+name+"."+ext)
#                 if os.path.exists(searchStr): 
#                     imgDouble = colour.read_image(searchStr, bit_depth='float32', method='Imageio') # <--- read thumbnail of input file

#                 else:
#                     if not os.path.exists(os.path.join(path,"thumbnails")): os.mkdir(os.path.join(path,"thumbnails"))

#                     # read image and create thumbnail
#                     imgDouble = colour.read_image(filename, bit_depth='float32', method='Imageio') # <--- read input file

#                     # resize to thumbnail size
#                     iY, iX, _ = imgDouble.shape
#                     maxX = processing.ProcessPipe.maxSize
#                     factor = maxX/iX
#                     imgDoubleFull = copy.deepcopy(imgDouble)
#                     imgThumbnail =  skimage.transform.resize(imgDouble, (int(iY * factor),maxX ))
#                     # save thumbnail
#                     colour.write_image(imgThumbnail,searchStr, method='Imageio')

#                     imgDouble = imgThumbnail

#             else:
#                 # thumb set to False, read input not the thumbnail
#                 imgDouble = colour.read_image(filename, bit_depth='float32', method='Imageio')

#             type = imageType.HDR
#             linear = True
#             scalingFactor = 1.0




        # Debugging: Output image min/max values
        print(f"Image written to {fileName} with min/max values: {np.min(self.cData)}, {np.max(self.cData)}")


    # -----------------------------------------------------------------
    def buildThumbnail(self: Image, maxSize :int= 800) -> Image:
        """build a thumbnail image."""
        
        y, x, _ =  self.cData.shape
        factor : int = maxSize/max(y,x)
        if factor<1:
            thumbcData = skimage.transform.resize(self.cData, (int(y * factor),int(x*factor) ))

            return Image(thumbcData, self.cSpace, self.hdr)
        else:
            return deepcopy(self)


    # static methods
    # -----------------------------------------------------------------
    @staticmethod
    def read(fileName : str) -> Image:
        """read image from system."""
        img : Image 
        path, name, ext = filenamesplit(fileName)
        if os.path.exists(fileName):
            if ext == "jpg":
                imgData :  np.ndarray = colour.read_image(fileName, bit_depth='float32', method= 'Imageio')
                img = Image(imgData, ColorSpace.sRGB, False)
            if ext == "hdr":
                imgData :  np.ndarray = colour.read_image(fileName, bit_depth='float32', method= 'Imageio')
                img = Image(imgData, ColorSpace.sRGB, True)
        else:
            img = Image(np.ones((600,800,3))*0.50, ColorSpace.sRGB, False)
        return img
    # -----------------------------------------------------------------


