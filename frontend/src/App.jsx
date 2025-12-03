import { useState } from "react";
import "./App.css";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [flashcards, setFlashcards] = useState([]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setQuestions(data.questions);
    setFlashcards(data.flashcards);

    setLoading(false);
  };

  return (
    <div className="container">
      <h1 className="title">Document Analyzer</h1>
      <p className="subtitle">
        Upload a document to generate technical questions and flashcards.
      </p>

      {/* Upload Section */}
      <div className="upload-box">
        <label className="upload-label">
          <span>Select a file</span>
          <input type="file" onChange={handleUpload} hidden />
        </label>
      </div>

      {loading && <p className="loading">Processing… Please wait.</p>}

      {/* QUESTIONS */}
      <h2 className="section-title">Generated Questions</h2>
      <div className="card-grid">
        {questions.map((q, i) => (
          <div className="tech-card" key={i}>
            <p>{q}</p>
          </div>
        ))}

        {questions.length === 0 && !loading && (
          <p className="empty">No questions yet.</p>
        )}
      </div>

      {/* FLASHCARDS */}
      <h2 className="section-title">Flashcards</h2>
      <div className="card-grid">
        {flashcards.map((f, i) => (
          <div className="tech-card flash" key={i}>
            <p className="cloze">{f.cloze}</p>
            <p className="answer">Answer: {f.answer}</p>
          </div>
        ))}

        {flashcards.length === 0 && !loading && (
          <p className="empty">No flashcards yet.</p>
        )}
      </div>
    </div>
  );
}
