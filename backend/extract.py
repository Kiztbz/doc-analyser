from PyPDF2 import PdfReader
import docx

def extract_text_from_pdf(bytes_data):
    import io
    reader = PdfReader(io.BytesIO(bytes_data))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(bytes_data):
    import io
    doc = docx.Document(io.BytesIO(bytes_data))
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_file(filename, bytes_data):
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(bytes_data)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(bytes_data)
    else:
        return bytes_data.decode("utf-8")
