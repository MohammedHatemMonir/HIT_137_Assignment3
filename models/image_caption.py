# Image captioning model using BLIP

from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from models.base_model import BaseAIModel


class ImageCaptionModel(BaseAIModel):
    # Image captioning model class
    
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base"):
        # Initialize image captioning model
        super().__init__(model_name)
        self._processor = None
        self._model = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def _load_model(self) -> None:
        # Load the BLIP model
        try:
            # Load BLIP processor and model
            self._processor = BlipProcessor.from_pretrained(self._model_name)
            self._model = BlipForConditionalGeneration.from_pretrained(
                self._model_name,
                torch_dtype=torch.float16 if self._device == "cuda" else torch.float32
            )
            self._model = self._model.to(self._device)
            
        except Exception as e:
            raise RuntimeError(f"Failed to load image captioning model: {str(e)}")
    
    def process(self, image: Image.Image) -> str:
        # Generate caption for image
        self._ensure_loaded()
        
        # Process image and generate caption
        inputs = self._processor(image, return_tensors="pt").to(self._device)
        
        with torch.no_grad():
            generated_ids = self._model.generate(
                **inputs,
                max_length=50,
                num_beams=5,
                early_stopping=True
            )
        
        caption = self._processor.decode(generated_ids[0], skip_special_tokens=True)
        return caption
    
    def process_with_conditional_text(self, image: Image.Image, conditional_text: str = "") -> str:
        # Generate caption with conditional text
        self._ensure_loaded()
        
        # Use conditional text if provided
        if conditional_text:
            inputs = self._processor(image, conditional_text, return_tensors="pt").to(self._device)
        else:
            inputs = self._processor(image, return_tensors="pt").to(self._device)
        
        with torch.no_grad():
            generated_ids = self._model.generate(
                **inputs,
                max_length=50,
                num_beams=5
            )
        
        caption = self._processor.decode(generated_ids[0], skip_special_tokens=True)
        return caption
    
    def analyze_image_features(self, image: Image.Image) -> dict:
        # Extract image features
        return {
            "size": image.size,
            "mode": image.mode,
            "format": getattr(image, 'format', 'Unknown'),
            "has_transparency": image.mode in ('RGBA', 'LA', 'P')
        }
    
    def get_model_info(self) -> dict:
        # Get model information
        info = super().get_model_info()
        info.update({
            "model_type": "Image Captioning (BLIP)",
            "device": self._device,
            "input_type": "PIL Image",
            "output_type": "Text Caption",
            "description": "Generates descriptive captions for input images using vision-language models"
        })
        return info