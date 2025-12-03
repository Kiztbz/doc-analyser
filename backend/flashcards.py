# backend/flashcards.py
import re
import threading
from sentence_transformers import util
from transformers import AutoTokenizer, T5ForConditionalGeneration

_embedder = None
_tokenizer = None
_qg_model = None
_lock = threading.Lock()


def _lazy_load_models():
    global _embedder, _tokenizer, _qg_model
    with _lock:
        if _embedder is None:
            from sentence_transformers import SentenceTransformer
            print("Loading SBERT embedder...")
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        if _tokenizer is None or _qg_model is None:
            print("Loading T5 tokenizer + model...")
            _tokenizer = AutoTokenizer.from_pretrained("t5-small", use_fast=True)
            _qg_model = T5ForConditionalGeneration.from_pretrained("t5-small")


def split_sentences(text):
    """A safe sentence splitter that works without NLTK."""
    raw = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in raw if s.strip()]


def extract_key_phrases(text, top_n=8):
    """Extract noun-heavy phrases WITHOUT NLTK."""
    sentences = split_sentences(text)
    phrases = set()

    for sent in sentences:
        words = sent.split()

        # heuristic noun phrase extractor
        np = []
        for w in words:
            if w[0].isupper() or len(w) > 6:  # simple concept heuristic
                np.append(w)
            else:
                if len(np) > 0:
                    phrases.add(" ".join(np))
                    np = []
        if len(np) > 0:
            phrases.add(" ".join(np))

    cleaned = [p.strip() for p in phrases if 3 <= len(p) <= 50]

    if not cleaned:
        return sentences[:top_n]

    _lazy_load_models()

    text_emb = _embedder.encode(text)
    phrase_embs = _embedder.encode(cleaned, batch_size=16)
    scores = [util.cos_sim(text_emb, pe).item() for pe in phrase_embs]
    sorted_phrases = [p for _, p in sorted(zip(scores, cleaned), reverse=True)]

    return sorted_phrases[:top_n]


def create_flashcards(text):
    _lazy_load_models()

    phrases = extract_key_phrases(text, top_n=8)

    prompt = (
        "Generate multiple high-quality study flashcards. "
        "Format each item as:\nQ: <question>\nA: <answer>\n\n"
        f"Concepts: {', '.join(phrases)}\n\n"
        f"Context:\n{text}"
    )

    enc = _tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)

    import torch
    with torch.no_grad():
        out = _qg_model.generate(
            enc["input_ids"],
            max_length=256,
            num_beams=4,
            temperature=0.7,
            early_stopping=True,
        )

    decoded = _tokenizer.decode(out[0], skip_special_tokens=True)

    # robust Q/A extraction
    pairs = re.findall(r"Q[:\-]?\s*(.*?)\s*A[:\-]?\s*(.*?)(?=(?:Q[:\-]|$))", decoded, re.DOTALL)
    flashcards = []

    for q, a in pairs:
        question = q.strip()
        answer = a.strip()
        if not question or not answer:
            continue

        # semantic similarity check
        try:
            q_emb = _embedder.encode(question)
            a_emb = _embedder.encode(answer)
            sim = float(util.cos_sim(q_emb, a_emb).item())
        except:
            sim = 0.0

        if sim < 0.10:  # lower threshold to avoid discarding too much
            continue

        flashcards.append({
            "question": question,
            "answer": answer,
            "score": sim,
        })

    flashcards.sort(key=lambda x: x["score"], reverse=True)
    return flashcards
