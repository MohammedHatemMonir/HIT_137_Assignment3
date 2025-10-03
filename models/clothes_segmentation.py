"""
================================================================================
CLOTHES SEGMENTATION MODEL - SEGFORMER-BASED CLOTHING DETECTION
================================================================================

OVERVIEW:
This module implements a clothing segmentation model using SegFormer, a 
transformer-based semantic segmentation architecture. The model can identify 
and segment different types of clothing items in images, producing colored 
overlay maps that highlight detected garments. This demonstrates computer 
vision capabilities integrated with Object-Oriented Programming principles.

CORE FUNCTIONALITY:
- Semantic segmentation of clothing items in input images
- Multi-class clothing detection (shirts, pants, shoes, accessories, etc.)
- Colored visualization of segmented clothing regions
- Confidence-based filtering to reduce false positives
- GPU acceleration support for faster processing

MODEL DETAILS:
- Architecture: SegFormer (Semantic Segmentation with Transformers)
- Pre-trained Model: "mattmdjaga/segformer_b2_clothes"
- Input: PIL Images (automatically converted to RGB)
- Output: Tuple of (overlay_image, colored_map_image)
- Device Support: CUDA (GPU) when available, falls back to CPU

CLOTHING CLASSES DETECTED:
The model tracks specific clothing categories defined in _clothing_ids_of_interest:
- Class 2: Upper body garments (shirts, jackets, etc.)
- Class 4: Lower body garments (pants, skirts, etc.)  
- Class 6: Accessories and outerwear
- Class 11: Footwear (shoes, boots, etc.)
- Class 14: Headwear (hats, caps, etc.)
- Class 15: Additional clothing items

OOP CONCEPTS DEMONSTRATED:
1. INHERITANCE: 
   - Inherits from BaseAIModel for common AI model functionality
   - Overrides abstract methods _load_model() and process()

2. ENCAPSULATION:
   - Private attributes for model components (_processor, _model, _device)
   - Internal methods for image processing and color assignment
   - Controlled access to model information through properties

3. POLYMORPHISM:
   - Implements BaseAIModel.process() with clothing-specific logic
   - Method overriding for specialized model information

4. DECORATOR PATTERN:
   - @validate_input for input validation
   - @log_operation for automatic logging
   - @error_handler for graceful error management

TECHNICAL IMPLEMENTATION:
- Uses Hugging Face Transformers library for model loading
- Implements bilinear interpolation for output resizing
- Applies confidence thresholding to filter uncertain predictions
- Generates deterministic color palette for consistent visualization
- Memory management with explicit model unloading

PROCESSING PIPELINE:
1. Input validation (expects dict with 'image' key containing PIL Image)
2. Model preprocessing (SegformerImageProcessor)
3. Forward pass through SegFormer network
4. Logits upsampling to original image resolution
5. Confidence filtering and class prediction
6. Color mapping for clothing regions only
7. Overlay generation (blend original + colored mask)

PERFORMANCE FEATURES:
- Lazy loading (model loaded only when first used)
- GPU acceleration when CUDA is available
- Memory-efficient processing with torch.no_grad()
- Explicit memory cleanup in unload_model()

ERROR HANDLING:
- Graceful handling of missing dependencies
- Input validation with descriptive error messages
- Device detection and fallback mechanisms
- Exception wrapping with decorator-based error handling

USAGE EXAMPLE:
    model = ClothesSegmentationModel()
    result = model.process({"image": pil_image})
    overlay_img, colored_img = result

REFERENCES:
- ChatGPT-5: Model implementation guidance and code review
- SegFormer Model: https://huggingface.co/mattmdjaga/segformer_b2_clothes
- Hugging Face Transformers: https://huggingface.co/docs/transformers/
- W3Schools Python OOP: https://www.w3schools.com/python/python_classes.asp
- SegFormer Paper: https://arxiv.org/abs/2105.15203
================================================================================
"""

# clothes segmentation model using segformer

from PIL import Image
import torch
import numpy as np
from typing import Any, Dict, Tuple

try:
    # newer versions use segformerimageprocessor instead of feature extractor
    from transformers import (
        SegformerImageProcessor as SegformerProcessor,
        AutoModelForSemanticSegmentation
    )
except Exception:
    SegformerProcessor = None
    AutoModelForSemanticSegmentation = None

from models.base_model import BaseAIModel
from gui.decorators import validate_input, log_operation, error_handler


class ClothesSegmentationModel(BaseAIModel):
    """find clothing pixels and color them"""

    def __init__(self, model_name: str = "mattmdjaga/segformer_b2_clothes"):
        # pick model + device
        super().__init__(model_name)
        self._processor = None  # image processor
        self._model = None      # segmentation net
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

    # class ids we care about
        self._clothing_ids_of_interest = [2, 4, 6, 11, 14, 15]

    def get_model_info(self) -> Dict[str, Any]:
        # model info dict
        info = super().get_model_info()
        info.update({
            "model_type": "Clothes Segmentation (SegFormer)",
            "device": self._device,
            "input_type": "PIL Image",
            "output_type": "PIL Image (colored clothing mask)",
            "description": "Segments clothing items from an image and colors only those regions"
        })
        return info

    def _load_model(self) -> None:
        # load processor + model
        if SegformerProcessor and AutoModelForSemanticSegmentation:
            self._processor = SegformerProcessor.from_pretrained(self._model_name)
            self._model = AutoModelForSemanticSegmentation.from_pretrained(
                self._model_name
            ).to(self._device)
            self._model.eval()  # set to eval mode
            return

    # if import failed earlier raise clearer error
        import transformers  # type: ignore
        raise ImportError(
            f"Could not load segmentation classes (transformers={getattr(transformers, '__version__', 'unknown')}). Try updating transformers."
        )

    @validate_input
    @log_operation
    @error_handler("Clothes segmentation failed")
    def process(self, data: Any) -> Tuple[Image.Image, Image.Image]:
        """return overlay + colored map for clothes. expects {'image': pil.image}"""
        # check input
        if not isinstance(data, dict) or "image" not in data:
            raise ValueError("Need a dict with key 'image' containing a PIL Image")

        image = data["image"]
        if not isinstance(image, Image.Image):
            raise TypeError("'image' must be a PIL Image")

        # ensure model is ready
        self._ensure_loaded()

        # prep tensor
        inputs = self._processor(images=image, return_tensors="pt").to(self._device)

        # forward pass
        with torch.no_grad():
            outputs = self._model(**inputs)

        # raw scores
        logits = outputs.logits  # shape: [batch, num_classes, H, W]
        # Resize to original image size (SegFormer internal size may differ)
        upsampled = torch.nn.functional.interpolate(
            logits,
            size=image.size[::-1],  # (H, W) order
            mode="bilinear",
            align_corners=False,
        )

        # class per pixel
        pred = upsampled.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)

        # confidence mask
        probs = torch.nn.functional.softmax(upsampled, dim=1)[0]
        confidence, _ = torch.max(probs, dim=0)
        confidence_mask = (confidence >= 0.5).cpu().numpy()

        # drop low confidence
        pred[~confidence_mask] = 0

        # only keep clothing classes we track
        clothing_mask = np.isin(pred, self._clothing_ids_of_interest)

        # empty rgb canvas
        color_result = np.zeros((pred.shape[0], pred.shape[1], 3), dtype=np.uint8)

        # simple deterministic color set
        num_classes = int(self._model.config.num_labels)
        rng = np.random.default_rng(42)
        palette = rng.integers(0, 255, size=(num_classes, 3), dtype=np.uint8)

        # assign colors on clothing mask
        color_result[clothing_mask] = palette[pred[clothing_mask]]

        # blend original + color for overlay
        orig_arr = np.array(image.convert("RGB"))
        overlay_arr = orig_arr.copy()
        alpha = 0.45
        overlay_arr[clothing_mask] = (
            (1 - alpha) * orig_arr[clothing_mask].astype(np.float32) +
            alpha * color_result[clothing_mask].astype(np.float32)
        ).astype(np.uint8)

        overlay_img = Image.fromarray(overlay_arr)
        colored_img = Image.fromarray(color_result)
        return overlay_img, colored_img

    def unload_model(self) -> None:
        # free memory for model and processor
        if self._model is not None:
            del self._model
            self._model = None
        self._processor = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
