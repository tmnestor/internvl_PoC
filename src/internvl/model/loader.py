"""
Model loading utilities for InternVL Evaluation

This module handles loading the InternVL model and tokenizer.
Supports both absolute paths and paths relative to project root.
"""

import os
from typing import Any, Tuple
from pathlib import Path

import torch
from transformers import AutoModel, AutoTokenizer

from src.internvl.utils.logging import get_logger
from src.internvl.utils.path import resolve_path, enforce_module_invocation

# Enforce module invocation pattern
enforce_module_invocation("src.internvl.model")

# Get logger for this module
logger = get_logger(__name__)

def load_model_and_tokenizer(
    model_path: str,
    device: str = "cpu",
    use_flash_attn: bool = False,
    trust_remote_code: bool = True,
    local_files_only: bool = False
) -> Tuple[Any, Any]:
    """
    Load InternVL model and tokenizer.
    Supports both HuggingFace model IDs and local paths (absolute or relative).

    Args:
        model_path: Path to model directory or HuggingFace model ID
        device: Device to load model on ('cuda' or 'cpu')
        use_flash_attn: Whether to use FlashAttention for faster inference
        trust_remote_code: Whether to trust remote code in model
        local_files_only: Whether to only use local files (for local models)

    Returns:
        Tuple of (model, tokenizer)
    """
    # Resolve model path if it's from environment variables
    env_model_path = os.environ.get("INTERNVL_MODEL_PATH")
    if env_model_path:
        resolved_path = resolve_path("MODEL_PATH")
        if resolved_path:
            model_path = str(resolved_path)
            logger.info(f"Using model path from environment: {model_path}")

    logger.info(f"Loading model from: {model_path}")

    # Determine if it's a local model path
    path_obj = Path(model_path)
    is_local_model = (path_obj.is_absolute() or model_path.startswith("./") or model_path.startswith("../")) and Path(model_path).exists()

    if is_local_model:
        logger.info("Using local model files")
        local_files_only = True
    
    # Configure loading parameters
    model_loading_args = {
        "torch_dtype": torch.bfloat16,
        "low_cpu_mem_usage": True,
        "use_flash_attn": use_flash_attn and device == "cuda",
        "trust_remote_code": trust_remote_code
    }
    
    if local_files_only:
        model_loading_args["local_files_only"] = True
    
    # Load tokenizer first
    tokenizer_config = {
        "trust_remote_code": trust_remote_code
    }
    
    if local_files_only:
        tokenizer_config["local_files_only"] = True
        
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path, **tokenizer_config)
        logger.info("Tokenizer loaded successfully")
    except Exception as e:
        logger.error(f"Error loading tokenizer: {e}")
        logger.info("Trying with minimal parameters...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    
    # Load model
    try:
        model = AutoModel.from_pretrained(model_path, **model_loading_args).eval()
        
        # Move model to appropriate device
        if device == "cuda" and torch.cuda.is_available():
            model = model.cuda()
            logger.info("Model loaded on GPU")
        else:
            if device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA requested but not available, using CPU instead")
            logger.info("Model loaded on CPU")
            
        return model, tokenizer
    
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        logger.info("Trying fallback loading...")
        
        # Fallback loading with simplified arguments
        fallback_args = {
            "trust_remote_code": True
        }
        
        if local_files_only:
            fallback_args["local_files_only"] = True
            
        model = AutoModel.from_pretrained(model_path, **fallback_args).eval()
        
        if device == "cuda" and torch.cuda.is_available():
            model = model.cuda()
            
        logger.info("Model loaded with fallback parameters")
        return model, tokenizer