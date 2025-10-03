# Text-to-image model using Stable Diffusion

from PIL import Image
import torch
from diffusers import StableDiffusionPipeline
from models.base_model import BaseAIModel


class TextToImageModel(BaseAIModel):
    # Text-to-image model class
    
    def __init__(self, model_name: str = "runwayml/stable-diffusion-v1-5"):
        # Initialize text-to-image model
        super().__init__(model_name)
        self._pipeline = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def _load_model(self) -> None:
        # Load the Stable Diffusion model
        try:
            # Load the diffusion pipeline with appropriate settings
            self._pipeline = StableDiffusionPipeline.from_pretrained(
                self._model_name,
                torch_dtype=torch.float16 if self._device == "cuda" else torch.float32,
                safety_checker=None,  # Disable safety checker for demo
                requires_safety_checker=False
            )
            self._pipeline = self._pipeline.to(self._device)
            
            # Enable memory efficient attention if available
            if hasattr(self._pipeline, "enable_attention_slicing"):
                self._pipeline.enable_attention_slicing()
            
        except Exception as e:
            raise RuntimeError(f"Failed to load text-to-image model: {str(e)}")
    
    def process(self, text_prompt: str) -> Image.Image:
        # Generate image from text prompt
        self._ensure_loaded()
        
        # Generate image using the loaded pipeline
        with torch.no_grad():
            result = self._pipeline(
                text_prompt,
                num_inference_steps=20,  # Faster generation for demo
                guidance_scale=7.5,
                height=512,
                width=512
            )
        
        return result.images[0]
    
    def generate_multiple(self, text_prompt: str, num_images: int = 2) -> list:
        # Generate multiple images
        self._ensure_loaded()
        
        images = []
        for i in range(num_images):
            image = self.process(text_prompt)
            images.append(image)
        
        return images
    
    def get_model_info(self) -> dict:
        # Get model information
        info = super().get_model_info()
        info.update({
            "model_type": "Text-to-Image (Stable Diffusion)",
            "device": self._device,
            "input_type": "Text",
            "output_type": "PIL Image",
            "description": "Generates images from text descriptions using diffusion models"
        })
        return info