import torch
import numpy as np
import os
from PIL import Image
from .draggen_client import DraggenClient, DraggenMoodboard
from .compositor import DraggenCompositor

# Helper to convert PIL to Tensor
def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

class DraggenLocalMoodboardLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "", "multiline": False}),
            },
        }

    RETURN_TYPES = ("DRAGGEN_MOODBOARD",)
    RETURN_NAMES = ("moodboard",)
    FUNCTION = "load_moodboard"
    CATEGORY = "Draggen"

    def load_moodboard(self, folder_path):
        client = DraggenClient()
        moodboard = client.load_local(folder_path)
        return (moodboard,)

class DraggenRemoteMoodboardLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "moodboard_id": ("STRING", {"default": ""}),
                "api_key": ("STRING", {"default": "", "multiline": False}),
            },
        }

    RETURN_TYPES = ("DRAGGEN_MOODBOARD",)
    RETURN_NAMES = ("moodboard",)
    FUNCTION = "load_moodboard"
    CATEGORY = "Draggen"

    def load_moodboard(self, moodboard_id, api_key):
        if not api_key:
            raise ValueError("API Key is required.")
            
        client = DraggenClient(api_key=api_key)
        moodboard = client.load_remote(moodboard_id)
        return (moodboard,)

class DraggenMoodboardRendered:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "moodboard": ("DRAGGEN_MOODBOARD",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "render"
    CATEGORY = "Draggen"

    def render(self, moodboard: DraggenMoodboard):
        image = DraggenCompositor.render(moodboard, base_path=moodboard.base_path)
        return (pil2tensor(image),)

class DraggenMoodboardImages:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "moodboard": ("DRAGGEN_MOODBOARD",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "get_images"
    CATEGORY = "Draggen"
    OUTPUT_IS_LIST = (True,)

    def get_images(self, moodboard: DraggenMoodboard):
        images = []
        for el in moodboard.elements:
            if el.type == 'image' and el.src:
                img = DraggenCompositor.get_image_from_url_or_path(el.src, base_path=moodboard.base_path)
                images.append(pil2tensor(img))
        
        if not images:
            # Return empty tensor batch? Comfy doesn't like empty.
            # Return a blank 1x1
            return ([torch.zeros((1, 64, 64, 3))],)
            
        # Returning a list of tensors creates a batch in Comfy if standard, 
        # or a list type if configured.
        # OUTPUT_IS_LIST = (True,) ensures it returns a list of individual images (generic list).
        # If we want a batch tensor, we stack them. But sizes might differ!
        # So List of images is safer.
        return (images,)

class DraggenMoodboardText:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "moodboard": ("DRAGGEN_MOODBOARD",),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_text"
    CATEGORY = "Draggen"

    def get_text(self, moodboard: DraggenMoodboard):
        texts = []
        for el in moodboard.elements:
            if el.type == 'text' and el.text:
                texts.append(el.text)
        
        full_text = "\n".join(texts)
        return (full_text,)
