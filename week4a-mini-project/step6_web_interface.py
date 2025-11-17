"""
Step 6: Web Interface
======================
Simple web interface for the QA system using FastAPI.

This step:
- Creates REST API for QA system
- Provides web UI for asking questions
- Allows document upload
- Shows answers with highlighting

Run: python step6_web_interface.py
Then visit: http://localhost:8000

Requirements: pip install fastapi uvicorn python-multipart
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import uvicorn

# Import our QA components
from step1_document_processor import DocumentProcessor
from step2_build_encoder import BERTEncoder, SimpleTokenizer
from step3_answer_extractor import AnswerExtractor
from step4_qa_engine import QuestionAnsweringEngine


# Initialize global QA engine (loaded once at startup)
qa_engine = None


class Question(BaseModel):
    """Question model for API."""
    text: str
    top_k: Optional[int] = 5


class Answer(BaseModel):
    """Answer model for API."""
    answer: str
    confidence: float
    source_document: Optional[str]
    context: Optional[str]


# Create FastAPI app
app = FastAPI(title="Question Answering System", version="1.0.0")


def initialize_qa_engine():
    """Initialize the QA engine with sample documents."""
    global qa_engine

    print("Initializing QA engine...")

    # Create document processor
    doc_processor = DocumentProcessor(max_chunk_length=512, chunk_overlap=50)

    # Load sample documents
    sample_dir = "sample_documents"
    if os.path.exists(sample_dir):
        doc_processor.add_documents_from_directory(sample_dir)
    else:
        print("Warning: sample_documents directory not found")

    # Create tokenizer
    tokenizer = SimpleTokenizer()
    all_texts = [chunk.text for chunk in doc_processor.chunks]
    if all_texts:
        tokenizer.fit(all_texts)

    # Create QA model (mini version for demo)
    vocab_size = len(tokenizer.vocab) if tokenizer.vocab else 1000
    encoder = BERTEncoder(
        vocab_size=vocab_size,
        d_model=128,
        num_heads=4,
        num_layers=2,
        d_ff=512
    )
    qa_model = AnswerExtractor(encoder)

    # Create QA engine
    qa_engine = QuestionAnsweringEngine(doc_processor, qa_model, tokenizer)

    print("✓ QA engine initialized!")
    return qa_engine


@app.on_event("startup")
async def startup_event():
    """Initialize QA engine on startup."""
    global qa_engine
    qa_engine = initialize_qa_engine()


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Question Answering System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #2196F3;
                text-align: center;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .question-box {
                margin: 20px 0;
            }
            input[type="text"] {
                width: 100%;
                padding: 12px;
                font-size: 16px;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            button {
                background-color: #2196F3;
                color: white;
                padding: 12px 30px;
                font-size: 16px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin-top: 10px;
            }
            button:hover {
                background-color: #1976D2;
            }
            .answer-box {
                margin-top: 30px;
                padding: 20px;
                background-color: #E3F2FD;
                border-left: 4px solid #2196F3;
                border-radius: 5px;
                display: none;
            }
            .answer-text {
                font-size: 18px;
                color: #1565C0;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .meta-info {
                font-size: 14px;
                color: #666;
                margin-top: 10px;
            }
            .confidence {
                display: inline-block;
                padding: 4px 10px;
                background-color: #4CAF50;
                color: white;
                border-radius: 3px;
                font-size: 12px;
            }
            .context {
                margin-top: 15px;
                padding: 15px;
                background-color: white;
                border-radius: 5px;
                font-size: 14px;
                color: #333;
            }
            .loading {
                text-align: center;
                color: #666;
                display: none;
            }
            .examples {
                margin-top: 20px;
                padding: 15px;
                background-color: #FFF3E0;
                border-radius: 5px;
            }
            .examples h3 {
                color: #F57C00;
                margin-top: 0;
            }
            .example-q {
                cursor: pointer;
                color: #0277BD;
                margin: 5px 0;
                padding: 5px;
            }
            .example-q:hover {
                background-color: #E1F5FE;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Question Answering System</h1>
            <p style="text-align: center; color: #666;">
                Ask questions about the knowledge base
            </p>

            <div class="question-box">
                <input type="text" id="question" placeholder="Type your question here..." />
                <button onclick="askQuestion()">Get Answer</button>
            </div>

            <div class="loading" id="loading">
                ⏳ Processing your question...
            </div>

            <div class="answer-box" id="answer-box">
                <div class="answer-text" id="answer"></div>
                <div class="meta-info">
                    <span class="confidence" id="confidence"></span>
                    <span id="source" style="margin-left: 15px;"></span>
                </div>
                <div class="context">
                    <strong>Context:</strong><br>
                    <span id="context"></span>
                </div>
            </div>

            <div class="examples">
                <h3>Example Questions:</h3>
                <div class="example-q" onclick="setQuestion('What is attention?')">
                    • What is attention?
                </div>
                <div class="example-q" onclick="setQuestion('What does BERT stand for?')">
                    • What does BERT stand for?
                </div>
                <div class="example-q" onclick="setQuestion('How do transformers work?')">
                    • How do transformers work?
                </div>
                <div class="example-q" onclick="setQuestion('What is multi-head attention?')">
                    • What is multi-head attention?
                </div>
            </div>
        </div>

        <script>
            function setQuestion(q) {
                document.getElementById('question').value = q;
            }

            async function askQuestion() {
                const question = document.getElementById('question').value.trim();

                if (!question) {
                    alert('Please enter a question');
                    return;
                }

                // Show loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('answer-box').style.display = 'none';

                try {
                    // Call API
                    const response = await fetch('/api/answer', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ text: question, top_k: 5 })
                    });

                    const data = await response.json();

                    // Hide loading
                    document.getElementById('loading').style.display = 'none';

                    // Show answer
                    document.getElementById('answer').innerText = data.answer;
                    document.getElementById('confidence').innerText =
                        'Confidence: ' + (data.confidence * 100).toFixed(1) + '%';
                    document.getElementById('source').innerText =
                        'Source: ' + (data.source_document || 'N/A');
                    document.getElementById('context').innerText =
                        data.context || 'No context available';

                    document.getElementById('answer-box').style.display = 'block';

                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    alert('Error: ' + error.message);
                }
            }

            // Allow Enter key to submit
            document.getElementById('question').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    askQuestion();
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content


@app.post("/api/answer", response_model=Answer)
async def get_answer(question: Question):
    """
    API endpoint to answer a question.
    """
    global qa_engine

    if qa_engine is None:
        return Answer(
            answer="QA engine not initialized",
            confidence=0.0,
            source_document=None,
            context=None
        )

    # Get answer
    result = qa_engine.get_best_answer(question.text, top_k_chunks=question.top_k)

    return Answer(
        answer=result['answer'],
        confidence=result['confidence'],
        source_document=result.get('source_document'),
        context=result.get('context')
    )


@app.get("/api/stats")
async def get_stats():
    """Get QA system statistics."""
    global qa_engine

    if qa_engine is None:
        return {"error": "QA engine not initialized"}

    stats = qa_engine.doc_processor.get_statistics()
    return {
        "num_documents": stats['num_documents'],
        "num_chunks": stats['num_chunks'],
        "vocabulary_size": len(qa_engine.tokenizer.vocab) if qa_engine.tokenizer.vocab else 0
    }


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a new document to the knowledge base."""
    global qa_engine

    if qa_engine is None:
        return {"error": "QA engine not initialized"}

    # Save uploaded file
    sample_dir = "sample_documents"
    os.makedirs(sample_dir, exist_ok=True)

    filepath = os.path.join(sample_dir, file.filename)
    content = await file.read()

    with open(filepath, 'wb') as f:
        f.write(content)

    # Add to document processor
    qa_engine.doc_processor.add_document(filepath)

    # Rebuild tokenizer
    all_texts = [chunk.text for chunk in qa_engine.doc_processor.chunks]
    qa_engine.tokenizer.fit(all_texts)

    return {
        "message": f"Document '{file.filename}' uploaded successfully",
        "total_documents": len(qa_engine.doc_processor.documents)
    }


def run_server():
    """
    Run the web server.
    """
    print("=" * 80)
    print("STEP 6: WEB INTERFACE")
    print("=" * 80)
    print("\nStarting QA system web server...")
    print("\n📊 Access the web interface at: http://localhost:8000")
    print("\n📡 API endpoints:")
    print("   POST /api/answer  - Answer a question")
    print("   GET  /api/stats   - Get system statistics")
    print("   POST /api/upload  - Upload a document")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run_server()
