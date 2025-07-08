# app.py - Simple RAG System for Task 1B
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import pdfplumber
import os
import json
import torch
from typing import List

app = FastAPI(title="RAG System", description="Simple RAG system for PDF/CSV ingestion")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    relevant_chunks: List[str]

class RAGSystem:
    def __init__(self):
        # Use small open-source models
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize small LLM for text generation
        print("Loading LLM model...")
        self.llm = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",
            device=0 if torch.cuda.is_available() else -1
        )
        print("LLM model loaded successfully!")
        
        self.chunks = []
        self.embeddings = None
        self.index = None
        
    def process_pdf(self, pdf_path: str) -> List[str]:
        """Extract text from PDF and chunk it"""
        chunks = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Simple chunking - split by sentences
                    sentences = text.split('.')
                    for sentence in sentences:
                        if len(sentence.strip()) > 20:  # Filter short sentences
                            chunks.append(sentence.strip())
        return chunks
    
    def process_csv(self, csv_path: str) -> List[str]:
        """Extract text from CSV and chunk it"""
        chunks = []
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            # Convert row to text
            row_text = ' '.join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
            if len(row_text) > 20:
                chunks.append(row_text)
        return chunks
    
    def create_embeddings(self, chunks: List[str]):
        """Create embeddings and FAISS index"""
        self.chunks = chunks
        self.embeddings = self.embedding_model.encode(chunks)
        
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))
    
    def query(self, query_text: str, top_k: int = 3) -> dict:
        """Query the RAG system"""
        if not self.index:
            return {"answer": "No documents loaded", "relevant_chunks": []}
        
        # Get query embedding
        query_embedding = self.embedding_model.encode([query_text])
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Get relevant chunks
        relevant_chunks = [self.chunks[idx] for idx in indices[0]]
        
        # Generate answer using LLM
        answer = self.generate_simple_answer(query_text, relevant_chunks)
        
        return {
            "answer": answer,
            "relevant_chunks": relevant_chunks
        }
    
    def generate_simple_answer(self, query: str, chunks: List[str]) -> str:
        """Generate answer using small LLM"""
        if not chunks:
            return "No relevant information found."
        
        # Combine top chunks as context
        context = "\n".join(chunks[:3])  # Use top 3 most relevant chunks
        
        # Create prompt for the LLM
        prompt = f"""Context: {context}

Question: {query}

Based on the context above, provide a concise answer to the question. If the context doesn't contain relevant information, say so clearly."""

        try:
            # Generate answer using the LLM
            response = self.llm(prompt, max_length=150, do_sample=True, temperature=0.7)
            answer = response[0]['generated_text']
            
            # Clean up the answer
            if answer.startswith(prompt):
                answer = answer[len(prompt):].strip()
            
            return answer if answer else "I couldn't generate a relevant answer based on the provided context."
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"Error generating answer, but here's the most relevant context: {chunks[0][:200]}..."

# Global RAG system instance
rag_system = RAGSystem()

def get_navigation_html():
    """Common navigation bar for all pages"""
    return """
    <nav style="background: #f8f9fa; padding: 10px; margin-bottom: 20px; border-radius: 5px;">
        <a href="/" style="text-decoration: none; margin-right: 20px; color: #007bff;">🏠 Home</a>
        <a href="/docs-page" style="text-decoration: none; margin-right: 20px; color: #007bff;">📄 Upload Docs</a>
        <a href="/query-page" style="text-decoration: none; margin-right: 20px; color: #007bff;">🔍 Query</a>
        <a href="/output-page" style="text-decoration: none; margin-right: 20px; color: #007bff;">📊 Output</a>
        <a href="/health" style="text-decoration: none; margin-right: 20px; color: #007bff;">💚 Status</a>
    </nav>
    """

def get_common_styles():
    """Common CSS styles for all pages"""
    return """
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        h2 { color: #666; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin: 15px 0; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; padding: 15px; border-radius: 5px; margin: 15px 0; border: 1px solid #bee5eb; }
        input[type="file"] { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; width: 100%; }
        textarea { width: 100%; height: 120px; margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; font-family: Arial, sans-serif; }
        .result { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff; }
        .chunk { background: #fff; margin: 10px 0; padding: 15px; border-radius: 5px; border: 1px solid #eee; }
        .loading { text-align: center; padding: 20px; color: #666; }
    </style>
    """

@app.get("/", response_class=HTMLResponse)
async def home_page():
    """Home page with overview"""
    nav_html = get_navigation_html()
    styles_html = get_common_styles()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RAG System - Home</title>
        """ + styles_html + """
    </head>
    <body>
        <div class="container">
            """ + nav_html + """
            
            <h1>🤖 RAG System Dashboard</h1>
            
            <div class="info">
                <h3>Welcome to the RAG (Retrieval-Augmented Generation) System!</h3>
                <p>This system helps you upload documents and ask questions about their content using AI.</p>
            </div>
            
            <h2>📋 How to Use:</h2>
            <ol style="font-size: 16px; line-height: 1.6;">
                <li><strong>Upload Documents:</strong> Go to the "Upload Docs" page to upload PDF or CSV files</li>
                <li><strong>Ask Questions:</strong> Use the "Query" page to ask questions about your uploaded documents</li>
                <li><strong>View Results:</strong> Check the "Output" page to see your query history and results</li>
                <li><strong>Check Status:</strong> Monitor system health and loaded documents</li>
            </ol>
            
            <h2>🔗 Quick Actions:</h2>
            <div style="display: flex; gap: 15px; margin: 20px 0;">
                <a href="/docs-page"><button>📄 Upload Documents</button></a>
                <a href="/query-page"><button>🔍 Ask Questions</button></a>
                <a href="/output-page"><button>📊 View Results</button></a>
            </div>
            
            <div id="system-status" class="info">
                <h3>📈 System Status</h3>
                <p>Loading system information...</p>
            </div>
        </div>
        
        <script>
            // Load system status
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('system-status').innerHTML = `
                        <h3>📈 System Status</h3>
                        <p><strong>Status:</strong> ${data.status}</p>
                        <p><strong>Documents Loaded:</strong> ${data.chunks_loaded} chunks</p>
                        <p><strong>Ready to process queries!</strong></p>
                    `;
                })
                .catch(error => {
                    document.getElementById('system-status').innerHTML = `
                        <h3>📈 System Status</h3>
                        <p class="error">Error loading status: ${error.message}</p>
                    `;
                });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/docs-page", response_class=HTMLResponse)
async def docs_page():
    """Document upload page"""
    nav_html = get_navigation_html()
    styles_html = get_common_styles()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RAG System - Upload Documents</title>
        """ + styles_html + """
    </head>
    <body>
        <div class="container">
            """ + nav_html + """
            
            <h1>📄 Upload Documents</h1>
            
            <div class="info">
                <p>Upload PDF or CSV files to add them to the knowledge base. The system will process and index your documents for querying.</p>
            </div>
            
            <h2>📎 Upload PDF File</h2>
            <form id="pdfForm" enctype="multipart/form-data">
                <input type="file" id="pdfFile" accept=".pdf" required>
                <button type="submit">Upload PDF</button>
            </form>
            <div id="pdfResult"></div>
            
            <h2>📊 Upload CSV File</h2>
            <form id="csvForm" enctype="multipart/form-data">
                <input type="file" id="csvFile" accept=".csv" required>
                <button type="submit">Upload CSV</button>
            </form>
            <div id="csvResult"></div>
            
            <h2>💡 Tips:</h2>
            <ul style="color: #666;">
                <li>PDF files will be processed to extract text content</li>
                <li>CSV files will be converted to searchable text format</li>
                <li>Larger files may take longer to process</li>
                <li>You can upload multiple files - they will be combined in the knowledge base</li>
            </ul>
        </div>
        
        <script>
            document.getElementById('pdfForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const fileInput = document.getElementById('pdfFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    document.getElementById('pdfResult').innerHTML = '<div class="error">Please select a PDF file</div>';
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                
                document.getElementById('pdfResult').innerHTML = '<div class="loading">Uploading and processing PDF...</div>';
                
                try {
                    const response = await fetch('/upload/pdf', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('pdfResult').innerHTML = '<div class="success">✅ ' + data.message + '</div>';
                        fileInput.value = '';
                    } else {
                        document.getElementById('pdfResult').innerHTML = '<div class="error">❌ Error: ' + data.detail + '</div>';
                    }
                } catch (error) {
                    document.getElementById('pdfResult').innerHTML = '<div class="error">❌ Upload failed: ' + error.message + '</div>';
                }
            });
            
            document.getElementById('csvForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const fileInput = document.getElementById('csvFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    document.getElementById('csvResult').innerHTML = '<div class="error">Please select a CSV file</div>';
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                
                document.getElementById('csvResult').innerHTML = '<div class="loading">Uploading and processing CSV...</div>';
                
                try {
                    const response = await fetch('/upload/csv', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('csvResult').innerHTML = '<div class="success">✅ ' + data.message + '</div>';
                        fileInput.value = '';
                    } else {
                        document.getElementById('csvResult').innerHTML = '<div class="error">❌ Error: ' + data.detail + '</div>';
                    }
                } catch (error) {
                    document.getElementById('csvResult').innerHTML = '<div class="error">❌ Upload failed: ' + error.message + '</div>';
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/query-page", response_class=HTMLResponse)
async def query_page():
    """Query interface page"""
    nav_html = get_navigation_html()
    styles_html = get_common_styles()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RAG System - Query</title>
        """ + styles_html + """
    </head>
    <body>
        <div class="container">
            """ + nav_html + """
            
            <h1>🔍 Ask Questions</h1>
            
            <div class="info">
                <p>Ask questions about your uploaded documents. The AI will search through the content and provide relevant answers.</p>
            </div>
            
            <form id="queryForm">
                <h2>💬 Your Question:</h2>
                <textarea id="query" placeholder="Example: 'What is the price of iPhone 15 Pro?' or 'How does AI help with software development?'"></textarea>
                <button type="submit">🔍 Search & Ask</button>
            </form>
            
            <div id="result"></div>
            
            <h2>💡 Example Questions:</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                <div>
                    <h3>📊 For CSV Data:</h3>
                    <ul style="color: #666;">
                        <li>"What products are available?"</li>
                        <li>"Which items cost less than $500?"</li>
                        <li>"Show me smartphone features"</li>
                        <li>"What are the latest releases?"</li>
                    </ul>
                </div>
                <div>
                    <h3>📄 For PDF Content:</h3>
                    <ul style="color: #666;">
                        <li>"What are the main topics discussed?"</li>
                        <li>"How can AI improve development?"</li>
                        <li>"What challenges are mentioned?"</li>
                        <li>"What tools are recommended?"</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <script>
            // Store query results for output page
            let queryHistory = JSON.parse(localStorage.getItem('queryHistory') || '[]');
            
            document.getElementById('queryForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const query = document.getElementById('query').value.trim();
                
                if (!query) {
                    document.getElementById('result').innerHTML = '<div class="error">Please enter a question</div>';
                    return;
                }
                
                document.getElementById('result').innerHTML = '<div class="loading">🤖 AI is thinking and searching...</div>';
                
                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({query: query})
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        // Store in history
                        const queryResult = {
                            query: query,
                            answer: data.answer,
                            chunks: data.relevant_chunks,
                            timestamp: new Date().toLocaleString()
                        };
                        queryHistory.unshift(queryResult);
                        localStorage.setItem('queryHistory', JSON.stringify(queryHistory.slice(0, 20))); // Keep last 20
                        
                        let chunksHtml = '';
                        data.relevant_chunks.forEach((chunk, i) => {
                            chunksHtml += '<div class="chunk"><strong>Source ' + (i+1) + ':</strong><br>' + chunk + '</div>';
                        });
                        
                        document.getElementById('result').innerHTML = 
                            '<div class="result">' +
                                '<h3>🤖 AI Answer:</h3>' +
                                '<p style="font-size: 16px; line-height: 1.6; background: white; padding: 15px; border-radius: 5px;">' + data.answer + '</p>' +
                                '<h3>📋 Relevant Information Found:</h3>' +
                                '<div style="max-height: 300px; overflow-y: auto;">' +
                                    chunksHtml +
                                '</div>' +
                                '<div style="margin-top: 20px;">' +
                                    '<a href="/output-page"><button>📊 View All Results</button></a>' +
                                '</div>' +
                            '</div>';
                        
                        // Clear form
                        document.getElementById('query').value = '';
                    } else {
                        document.getElementById('result').innerHTML = '<div class="error">❌ Error: ' + data.detail + '</div>';
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = '<div class="error">❌ Query failed: ' + error.message + '</div>';
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/output-page", response_class=HTMLResponse)
async def output_page():
    """Output and history page"""
    nav_html = get_navigation_html()
    styles_html = get_common_styles()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RAG System - Output & History</title>
        """ + styles_html + """
    </head>
    <body>
        <div class="container">
            """ + nav_html + """
            
            <h1>📊 Query Results & History</h1>
            
            <div style="display: flex; gap: 15px; margin: 20px 0;">
                <button onclick="loadHistory()">🔄 Refresh History</button>
                <button onclick="clearHistory()" style="background: #dc3545;">🗑️ Clear History</button>
                <button onclick="exportHistory()" style="background: #28a745;">💾 Export Results</button>
            </div>
            
            <div id="historyContent">
                <div class="loading">Loading query history...</div>
            </div>
        </div>
        
        <script>
            function loadHistory() {
                const history = JSON.parse(localStorage.getItem('queryHistory') || '[]');
                const container = document.getElementById('historyContent');
                
                if (history.length === 0) {
                    container.innerHTML = 
                        '<div class="info">' +
                            '<h3>📝 No queries yet</h3>' +
                            '<p>Start by uploading documents and asking questions!</p>' +
                            '<a href="/docs-page"><button>📄 Upload Documents</button></a>' +
                            '<a href="/query-page"><button>🔍 Ask Questions</button></a>' +
                        '</div>';
                    return;
                }
                
                let historyHtml = 
                    '<div class="info">' +
                        '<h3>📈 Query Statistics</h3>' +
                        '<p>Total queries: <strong>' + history.length + '</strong> | Latest: <strong>' + (history[0] ? history[0].timestamp : '') + '</strong></p>' +
                    '</div>';
                
                history.forEach((item, index) => {
                    let chunksHtml = '';
                    item.chunks.forEach((chunk, i) => {
                        chunksHtml += '<div class="chunk"><strong>Source ' + (i+1) + ':</strong><br>' + chunk + '</div>';
                    });
                    
                    historyHtml += 
                        '<div class="result" style="margin-bottom: 30px;">' +
                            '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">' +
                                '<h3>🔍 Query #' + (index + 1) + '</h3>' +
                                '<small style="color: #666;">' + item.timestamp + '</small>' +
                            '</div>' +
                            '<div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 15px;">' +
                                '<strong>Question:</strong><br>' + item.query +
                            '</div>' +
                            '<div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin-bottom: 15px;">' +
                                '<strong>🤖 AI Answer:</strong><br>' + item.answer +
                            '</div>' +
                            '<details>' +
                                '<summary style="cursor: pointer; color: #007bff; margin-bottom: 10px;">📋 View Source Information (' + item.chunks.length + ' chunks)</summary>' +
                                '<div style="max-height: 200px; overflow-y: auto;">' + chunksHtml + '</div>' +
                            '</details>' +
                        '</div>';
                });
                
                container.innerHTML = historyHtml;
            }
            
            function clearHistory() {
                if (confirm('Are you sure you want to clear all query history?')) {
                    localStorage.removeItem('queryHistory');
                    loadHistory();
                }
            }
            
            function exportHistory() {
                const history = JSON.parse(localStorage.getItem('queryHistory') || '[]');
                if (history.length === 0) {
                    alert('No history to export');
                    return;
                }
                
                const dataStr = JSON.stringify(history, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'rag_query_history_' + new Date().toISOString().split('T')[0] + '.json';
                link.click();
                URL.revokeObjectURL(url);
            }
            
            // Load history on page load
            loadHistory();
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # Save uploaded file
    file_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Process PDF
        chunks = rag_system.process_pdf(file_path)
        rag_system.create_embeddings(chunks)
        
        return {"message": f"PDF processed successfully. {len(chunks)} chunks created."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and process CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    # Save uploaded file
    file_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Process CSV
        chunks = rag_system.process_csv(file_path)
        rag_system.create_embeddings(chunks)
        
        return {"message": f"CSV processed successfully. {len(chunks)} chunks created."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query the RAG system"""
    try:
        result = rag_system.query(request.query)
        return QueryResponse(
            answer=result["answer"],
            relevant_chunks=result["relevant_chunks"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "chunks_loaded": len(rag_system.chunks)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)