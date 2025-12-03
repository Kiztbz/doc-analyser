# backend/qg.py
from transformers import AutoTokenizer, T5ForConditionalGeneration
import threading

_qg_tokenizer = None
_qg_model = None
_qg_lock = threading.Lock()

def _lazy_load_qg():
    global _qg_tokenizer, _qg_model
    with _qg_lock:
        if _qg_tokenizer is None:
            print("Loading QG tokenizer & model...")
            _qg_tokenizer = AutoTokenizer.from_pretrained("t5-small", use_fast=True)
            _qg_model = T5ForConditionalGeneration.from_pretrained("t5-small")

def generate_questions(text, chunk_size=400):
    _lazy_load_qg()
    # simple chunk split on words
    words = text.split()
    chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    results = []
    import torch
    for chunk in chunks[:6]:  # limit number of chunks to avoid very long runs
        prompt = "generate question: " + chunk
        enc = _qg_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            out = _qg_model.generate(enc["input_ids"], max_length=64, num_beams=4, early_stopping=True)
        q = _qg_tokenizer.decode(out[0], skip_special_tokens=True)
        if q and len(q) > 5:
            results.append(q.strip())
    return results
