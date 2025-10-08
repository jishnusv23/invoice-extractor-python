import instructor
from openai import OpenAI
import fitz  
import base64
import io
from typing import List, Dict, Any
from PIL import Image, ImageEnhance, ImageFilter
import logging

from src.config.config import Config
from src.models.aircraft_models import AircraftUtilization

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


base_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=Config.OPENROUTER_API_KEY
)
client = instructor.from_openai(base_client)


def pdf_to_images(pdf_path: str, dpi: int = 450) -> List[Image.Image]:
    """
    Convert PDF pages to optimized images for vision LLM
    
    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution (450 recommended for aircraft data precision)
        
    Returns:
        List of optimized PIL Image objects
    """
    try:
        doc = fitz.open(pdf_path)
        images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            
            img = _optimize_image_for_ocr(img)
            images.append(img)
        
        doc.close()
        logger.info(f"✅ Converted PDF to {len(images)} optimized images at {dpi} DPI")
        return images
        
    except Exception as e:
        logger.error(f"❌ Error converting PDF to images: {e}")
        return []


def _optimize_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    Optimize image for better OCR accuracy
    Critical for accurate extraction of decimal values in aircraft data
    """
    try:
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        
        contrast_enhancer = ImageEnhance.Contrast(image)
        image = contrast_enhancer.enhance(1.2)
        
        
        sharpness_enhancer = ImageEnhance.Sharpness(image)
        image = sharpness_enhancer.enhance(1.3)
        
        
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=2))
        
        
        brightness_enhancer = ImageEnhance.Brightness(image)
        image = brightness_enhancer.enhance(1.05)
        
        return image
        
    except Exception as e:
        logger.warning(f"⚠️ Error optimizing image: {e}, returning original")
        return image


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    try:
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        logger.error(f"❌ Error converting image to base64: {e}")
        return None


def prepare_image_content(images: List[Image.Image]) -> List[Dict[str, Any]]:
    """Prepare images in format required by Vision LLM API"""
    image_content = []
    
    for image in images:
        base64_image = image_to_base64(image)
        if base64_image:
            image_content.append({
                "type": "image_url",
                "image_url": {
                    "url": base64_image
                }
            })
    
    return image_content


def extract_aircraft_from_pdf(file_path: str, prompt: str, dpi: int = 450) -> AircraftUtilization:
    """
    Extract aircraft data from PDF using Vision LLM
    
    Args:
        file_path: Path to the PDF file
        prompt: Extraction instructions
        dpi: Image resolution (default 450 for high precision)
        
    Returns:
        AircraftUtilization data object
    """
    try:
        logger.info(f"\n🔄 Processing PDF: {file_path}")
        
        
        images = pdf_to_images(file_path, dpi=dpi)
        
        if not images:
            raise ValueError("Could not convert PDF to images")
        
        
        image_content = prepare_image_content(images)
        
        
        content = [{"type": "text", "text": prompt}] + image_content
        
        logger.info("🤖 Sending to Vision LLM for extraction...")
        
        
        aircraft_data = client.chat.completions.create(
            model=Config.VISION_MODEL,
            response_model=AircraftUtilization,
            max_retries=Config.MAX_RETRIES,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI that extracts structured aircraft utilization data from maintenance report images. Carefully analyze all visual elements including text, tables, charts, stamps, and handwritten notes. Extract all information accurately according to the schema provided."
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            temperature=Config.TEMPERATURE,
        )
        
        logger.info("✅ Data extracted and validated successfully")
        return aircraft_data
        
    except Exception as e:
        logger.error(f"❌ Error in extraction: {str(e)}")
        raise