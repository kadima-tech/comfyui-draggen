import os
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Position:
    x: float
    y: float

@dataclass
class Size:
    width: float
    height: float

@dataclass
class DraggenElement:
    id: str
    type: str # 'image', 'text', 'box'
    position: Position
    size: Size
    z_index: int
    src: Optional[str] = None
    text: Optional[str] = None
    color: Optional[str] = None
    fill_color: Optional[str] = None
    border_color: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        pos = data.get('position', {'x': 0, 'y': 0})
        size = data.get('size', {'width': 0, 'height': 0})
        return cls(
            id=data.get('id', ''),
            type=data.get('type', 'unknown'),
            position=Position(x=pos.get('x', 0), y=pos.get('y', 0)),
            size=Size(width=size.get('width', 0), height=size.get('height', 0)),
            z_index=data.get('zIndex', 0),
            src=data.get('src'),
            text=data.get('text'),
            color=data.get('color'),
            fill_color=data.get('fillColor'),
            border_color=data.get('borderColor')
        )

@dataclass
class DraggenMoodboard:
    id: str
    name: str
    elements: List[DraggenElement]
    viewport: Dict[str, Any]
    base_path: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], base_path: str = None):
        # Handle different response structures
        if 'board' in data:
            # Remote API single board response
            doc = data['board']
        elif 'projects' in data and isinstance(data['projects'], list) and len(data['projects']) > 0:
            # Local Export format: {"projects": [...]}
            doc = data['projects'][0]
        elif 'document' in data:
            # Legacy/Initial assumption
            doc = data['document']
        else:
            doc = data # Fallback if it's the raw object

        elements = [DraggenElement.from_dict(el) for el in doc.get('elements', [])]
        # Sort by zIndex
        elements.sort(key=lambda x: x.z_index)
        
        return cls(
            id=doc.get('id', ''),
            name=doc.get('name', 'Untitled'),
            elements=elements,
            viewport=doc.get('viewport', {}),
            base_path=base_path
        )
        # Sort by zIndex
        elements.sort(key=lambda x: x.z_index)
        
        return cls(
            id=doc.get('id', ''),
            name=doc.get('name', 'Untitled'),
            elements=elements,
            viewport=doc.get('viewport', {}),
            base_path=base_path
        )

class DraggenClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        # Use new domain: draggen.io
        self.api_base = "https://draggen.io/api/ext"

    def load_local(self, folder_path: str) -> DraggenMoodboard:
        """
        Loads a moodboard from a local folder.
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        json_file = None
        for file in os.listdir(folder_path):
            if file.endswith('.json'):
                json_file = os.path.join(folder_path, file)
                break
        
        if not json_file:
             raise FileNotFoundError(f"No .json file found in {folder_path}")
             
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return DraggenMoodboard.from_dict(data, base_path=folder_path)

    def load_remote(self, moodboard_id: str) -> DraggenMoodboard:
        """
        Fetches a moodboard from the API.
        """
        if not self.api_key:
            raise ValueError("API Key required for remote loading.")
        
        url = f"{self.api_base}/boards/{moodboard_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return DraggenMoodboard.from_dict(data)

    def list_boards(self) -> List[Dict[str, Any]]:
        """
        Lists available moodboards.
        """
        if not self.api_key:
            raise ValueError("API Key required for listing boards.")
            
        url = f"{self.api_base}/boards"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return data.get("boards", [])

