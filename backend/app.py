# backend/app.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from extract import extract_text_from_file
from qg import generate_questions
from flashcards import create_flashcards
import traceback

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text = extract_text_from_file(file.filename, contents)
        print("=== Received document (first 400 chars) ===")
        print(text[:400].replace("\n", " "))

        questions = generate_questions(text)
        print("Generated questions count:", len(questions))

        flashcards = create_flashcards(text)
        print("Generated flashcards count:", len(flashcards))

        return {"questions": questions, "flashcards": flashcards}
    except Exception as e:
        print("ERROR during analyze_document:", e)
        traceback.print_exc()
        return {"questions": [], "flashcards": [], "error": str(e)}
