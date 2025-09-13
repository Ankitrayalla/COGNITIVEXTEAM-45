from functools import lru_cache
from typing import Callable
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import os

MODEL_ID = "ibm-granite/granite-3.3-2b-instruct"

@lru_cache(maxsize=1)
def load_rewriter_model(model_id: str = MODEL_ID) -> Callable:
    """
    Load the ibm-granite instruction-following model and return a text-generation pipeline.
    This function is cached so it loads once.
    """
    # If you need to use an auth token, set environment variable HF_API_TOKEN before running.
    hf_token = os.getenv("HF_API_TOKEN", None)
    tok = AutoTokenizer.from_pretrained(model_id, use_fast=True, use_auth_token=hf_token)
    model = AutoModelForCausalLM.from_pretrained(model_id, use_auth_token=hf_token)
    # device: 0 for GPU, -1 for CPU
    device = 0 if _has_gpu() else -1
    gen = pipeline("text-generation", model=model, tokenizer=tok, device=device)
    return gen

def _has_gpu() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False

def rewrite_text(gen_pipeline: Callable, text: str, tone: str, max_length: int = 512) -> str:
    if not text.strip():
        return ""

    instruction = (
        f"You are an expert editor. Rewrite the input text to sound {tone}. "
        "Preserve the original meaning and factual content exactly, but improve flow, clarity, and expressiveness. "
        "Keep the rewritten version roughly the same length unless necessary. "
        "Respond only with the rewritten text.\n\nInput:\n" + text
    )

    gen_out = gen_pipeline(instruction, max_new_tokens=max_length, do_sample=False, num_return_sequences=1)
    out = gen_out[0].get("generated_text", "")

    # Try to strip the instruction if echoed
    if instruction.strip() in out:
        out = out.split(instruction.strip(), 1)[-1].strip()
    if "Input:" in out:
        out = out.split("Input:", 1)[0].strip()
    return out
