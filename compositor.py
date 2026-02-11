from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import os
from .draggen_client import DraggenMoodboard, DraggenElement

class DraggenCompositor:
    @staticmethod
    def get_image_from_url_or_path(src: str, base_path: str = None) -> Image.Image:
        """
        Resolves an image source to a PIL Image.
        Handles both remote URLs and local file paths.
        Prioritizes local file if base_path is provided and file exists.
        """
        try:
            # 1. Try resolving locally if base_path is set
            if base_path:
                # Strategy A: src is a relative path (e.g. "images/foo.png")
                candidates = [
                    os.path.join(base_path, src), 
                    os.path.join(base_path, 'images', os.path.basename(src)),
                    os.path.join(base_path, os.path.basename(src))
                ]
                
                # If src is a URL, extracting basename might give "foo.png" from "http://.../foo.png"
                if src.startswith('http'):
                    from urllib.parse import urlparse
                    path = urlparse(src).path
                    filename = os.path.basename(path)
                    candidates.append(os.path.join(base_path, 'images', filename))
                    candidates.append(os.path.join(base_path, filename))
                
                for path in candidates:
                    if os.path.exists(path) and os.path.isfile(path):
                        return Image.open(path).convert("RGBA")

            # 2. Fallback to URL fetch
            if src.startswith('http'):
                response = requests.get(src)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
            else:
                # Local file fallback (absolute path or relative without base_path somehow)
                img = Image.open(src)
            
            return img.convert("RGBA")
        except Exception as e:
            print(f"Failed to load image {src}: {e}")
            return Image.new("RGBA", (100, 100), (255, 0, 0, 255)) # Error placeholder

    @staticmethod
    def render(moodboard: DraggenMoodboard, base_path: str = None) -> Image.Image:
        # 1. Determine canvas size
        # We can either use a fixed size or calculate bounding box of all elements.
        # The user JSON shows x/y positions, some negative.
        # Let's calculate the bounding box.
        
        min_x = 0
        min_y = 0
        max_x = 1000
        max_y = 1000
        
        if moodboard.elements:
            min_x = min(el.position.x for el in moodboard.elements)
            min_y = min(el.position.y for el in moodboard.elements)
            max_x = max(el.position.x + el.size.width for el in moodboard.elements)
            max_y = max(el.position.y + el.size.height for el in moodboard.elements)
        
        # Add some padding
        padding = 50
        width = int(max_x - min_x + padding * 2)
        height = int(max_y - min_y + padding * 2)
        
        # Create canvas
        # Default background color? Let's assume transparent or white.
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        
        # 2. Draw elements in order (already sorted by zIndex in load)
        for el in moodboard.elements:
            # Calculate dest position relative to canvas (shifting by min_x/min_y)
            dest_x = int(el.position.x - min_x + padding)
            dest_y = int(el.position.y - min_y + padding)
            dest_w = int(el.size.width)
            dest_h = int(el.size.height)
            
            if el.type == 'image' and el.src:
                img = DraggenCompositor.get_image_from_url_or_path(el.src, base_path)
                img = img.resize((dest_w, dest_h), Image.Resampling.LANCZOS)
                canvas.alpha_composite(img, (dest_x, dest_y))
                
            elif el.type == 'box':
                # Parse colors
                fill = el.fill_color if el.fill_color else None
                outline = el.border_color if el.border_color else None
                # Create a rectangle
                # PIL Draw.rectangle doesn't support alpha in fill color string directly if it's hex without alpha?
                # User hex: #1a1a2e. We might need to assume alpha=255.
                
                # Helper to parse hex
                def parse_color(c):
                    if not c: return None
                    c = c.lstrip('#')
                    return tuple(int(c[i:i+2], 16) for i in (0, 2, 4)) + (255,)
                
                fill_rgba = parse_color(fill)
                outline_rgba = parse_color(outline)
                
                shape_layer = Image.new("RGBA", (width, height), (0,0,0,0))
                shape_draw = ImageDraw.Draw(shape_layer)
                shape_draw.rectangle(
                    [dest_x, dest_y, dest_x + dest_w, dest_y + dest_h],
                    fill=fill_rgba,
                    outline=outline_rgba,
                    width=1 # user provided borderWidth in json, but simplified for now
                )
                canvas.alpha_composite(shape_layer)

            elif el.type == 'text' and el.text:
                # Text rendering is complex without specific fonts.
                # Attempt to load a default font.
                # For now, minimal implementation.
                try:
                    font = ImageFont.truetype("arial.ttf", size=24) # System font assumption
                except:
                    font = ImageFont.load_default()
                
                # Text color
                fill = el.color if el.color else "#000000"
                
                draw.text((dest_x, dest_y), el.text, font=font, fill=fill)
        
        return canvas
