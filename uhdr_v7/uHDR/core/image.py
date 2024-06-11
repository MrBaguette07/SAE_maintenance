# image.py
from __future__ import annotations
from core.colourSpace import ColorSpace
from copy import deepcopy
import numpy as np
import os
import colour
import skimage.transform
import matplotlib
import json

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
        print(f"Image initialized with data shape: {data.shape}, min: {data.min()}, max: {data.max()}")
    
    def __repr__(self: Image) -> str:
        y, x, c = self.cData.shape
        res: str = '-------------------    Image   -------------------------------'
        res += f'\n size: {x} x {y} x {c} '
        res += f'\n colourspace: {self.cSpace.name}'
        res += f'\n hdr: {self.hdr}'
        res += f'\n Shape: {self.cData.shape}'
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
        if isinstance(self.cData, np.ndarray):
            self.cData = np.clip(self.cData * (1 + value), 0, 1)
            print(f"Exposure adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustContrastScaling(self, value: float):
        if isinstance(self.cData, np.ndarray):
            factor = (259 * (value + 255)) / (255 * (259 - value))
            self.cData = np.clip(factor * (self.cData - 0.5) + 0.5, 0, 1)
            print(f"Contrast scaling adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustContrastOffset(self, value: float):
        if isinstance(self.cData, np.ndarray):
            self.cData = np.clip(self.cData + value, 0, 1)
            print(f"Contrast offset adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustLightnessRange(self, value: tuple):
        if isinstance(self.cData, np.ndarray):
            min_light, max_light = value
            self.cData = np.clip((self.cData - min_light) / (max_light - min_light), 0, 1)
            print(f"Lightness range adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustHueShift(self, value: float):
        if isinstance(self.cData, np.ndarray):
            hsv = self.rgb_to_hsv(self.cData)
            hsv[..., 0] = (hsv[..., 0] + value) % 1.0
            self.cData = self.hsv_to_rgb(hsv)
            print(f"Hue shift adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustSaturation(self, value: float):
        if isinstance(self.cData, np.ndarray):
            hsv = self.rgb_to_hsv(self.cData)
            hsv[..., 1] = np.clip(hsv[..., 1] * (1 + value), 0, 1)
            self.cData = self.hsv_to_rgb(hsv)
            print(f"Saturation adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustColorExposure(self, value: float):
        if isinstance(self.cData, np.ndarray):
            self.cData = np.clip(self.cData * (1 + value), 0, 1)
            print(f"Color exposure adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustColorContrast(self, value: float):
        if isinstance(self.cData, np.ndarray):
            factor = (259 * (value + 255)) / (255 * (259 - value))
            self.cData = np.clip(factor * (self.cData - 0.5) + 0.5, 0, 1)
            print(f"Color contrast adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustHighlights(self, value: float):
        if isinstance(self.cData, np.ndarray):
            mask = self.cData > 0.8
            self.cData[mask] = np.clip(self.cData[mask] * (1 + value), 0, 1)
            print(f"Highlights adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustShadows(self, value: float):
        if isinstance(self.cData, np.ndarray):
            mask = self.cData < 0.2
            self.cData[mask] = np.clip(self.cData[mask] * (1 + value), 0, 1)
            print(f"Shadows adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustWhites(self, value: float):
        if isinstance(self.cData, np.ndarray):
            mask = self.cData > 0.9
            self.cData[mask] = np.clip(self.cData[mask] * (1 + value), 0, 1)
            print(f"Whites adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustBlacks(self, value: float):
        if isinstance(self.cData, np.ndarray):
            mask = self.cData < 0.1
            self.cData[mask] = np.clip(self.cData[mask] * (1 + value), 0, 1)
            print(f"Blacks adjusted: min {self.cData.min()}, max {self.cData.max()}")

    def adjustMediums(self, value: float):
        if isinstance(self.cData, np.ndarray):
            mask = (self.cData >= 0.2) & (self.cData <= 0.8)
            self.cData[mask] = np.clip(self.cData[mask] * (1 + value), 0, 1)
            print(f"Mediums adjusted: min {self.cData.min()}, max {self.cData.max()}")

    @staticmethod
    def rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
        """Convert RGB to HSV"""
        return matplotlib.colors.rgb_to_hsv(rgb)

    @staticmethod
    def hsv_to_rgb(hsv: np.ndarray) -> np.ndarray:
        """Convert HSV to RGB"""
        return matplotlib.colors.hsv_to_rgb(hsv)

    def apply_json_operations(image_data, json_path='image_operations.json'):
        with open(json_path, 'r') as file:
            operations = [json.loads(line) for line in file]
        
        for operation in operations:
            if operation['operation'] == 'convert':
                if operation['from'] == 'XYZ' and operation['to'] == 'sRGB':
                    image_data = colour.XYZ_to_sRGB(
                        image_data,
                        illuminant=np.array([0.3127, 0.329]),
                        chromatic_adaptation_transform='CAT02',
                        apply_cctf_encoding=operation.get('apply_cctf_encoding', True)
                    )
                elif operation['from'] == 'sRGB' and operation['to'] == 'XYZ':
                    image_data = colour.sRGB_to_XYZ(
                        image_data,
                        illuminant=np.array([0.3127, 0.329]),
                        chromatic_adaptation_transform='CAT02',
                        apply_cctf_decoding=operation.get('apply_cctf_decoding', True)
                    )
        return image_data