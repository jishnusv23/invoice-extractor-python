import os 
import base64
from pathlib import Path
from typing import Tuple

def read_invoice_file_as_base64(file_path:str)->str:
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found:{file_path}")
    
    validate_file_type(file_path)
    
    with open (file_path,"rb") as f :
        file_buffer=f.read()

    base64_data=base64.b64decode(file_buffer).decode('utf-8')
    mime_type=get_mime_type(file_path)

    return f"data:{mime_type};base64,{base64_data}"

def get_mime_type(file_path:str)->str:
   

    ext=Path(file_path).suffix.lower()

    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.pdf': 'application/pdf'
    }

    mime_type=mime_types.get(ext)

    if not mime_type:
        supported=', '.join(mime_types.keys())
        raise ValueError(f"Unsupported file type:{ext}.Supported:{supported}")
    
    return mime_type

def is_image(file_path:str)->bool:
    """Check if the file is an image"""
    ext=Path(file_path).suffix.lower()
    return ext in ['.jpg','.png','.jpeg','.gif','.web']

def validate_file_type(file_path: str) -> None:
  
    ext = Path(file_path).suffix.lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf']
    
    if ext not in valid_extensions:
        raise ValueError(
            f"Invalid file type: {ext}. Supported: {', '.join(valid_extensions)}"
        )


def read_file_as_buffer(file_path: str) -> Tuple[bytes, str]:
    
    validate_file_type(file_path)
    
    with open(file_path, 'rb') as f:
        file_buffer = f.read()
    
    mime_type = get_mime_type(file_path)
    
    return file_buffer, mime_type