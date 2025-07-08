# Task 1B: RAG-style LLM Pipeline (Mini POC)

## 🎯 Overview

This is a complete Retrieval-Augmented Generation (RAG) system that allows users to upload PDF/CSV documents and ask questions about their content using AI. The system uses small open-source models and provides a web interface for easy interaction.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │   FastAPI Server │    │   RAG Engine    │
│                 │    │                  │    │                 │
│ • Upload Pages  │◄──►│ • File Upload    │◄──►│ • PDF/CSV Parse │
│ • Query Page    │    │ • Query API      │    │ • Embeddings    │
│ • Results Page  │    │ • Health Check   │    │ • FAISS Vector  │
│ • Navigation    │    │ • Error Handling │    │ • LLM Generate  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔧 Components

### 1. Document Processing
- **PDF Handler**: Extracts text using `pdfplumber`
- **CSV Handler**: Converts tabular data to searchable text
- **Text Chunking**: Splits content into manageable pieces

### 2. Vector Storage
- **Embeddings**: `all-MiniLM-L6-v2` for semantic embeddings
- **Vector DB**: FAISS for fast similarity search
- **Indexing**: Automatic index creation and updates

### 3. Language Model
- **LLM**: `google/flan-t5-small` for text generation
- **Context**: Uses top-3 relevant chunks for answer generation
- **Fallback**: Graceful handling when no relevant content found

### 4. Web Interface
- **Upload Pages**: Separate interfaces for PDF and CSV
- **Query Interface**: Natural language question input
- **Results Display**: Shows AI answers with source information
- **History Tracking**: Local storage of query history

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd task1b-rag-system

# Build and run with Docker Compose
docker-compose up --build

# Access the application
open http://localhost:8000
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create uploads directory
mkdir uploads

# Run the application
python app.py

# Access at http://localhost:8000
```

## 📖 How to Use

### Step 1: Upload Documents
1. Navigate to "Upload Docs" page
2. Upload PDF files (research papers, articles, manuals)
3. Upload CSV files (data tables, product catalogs)
4. Wait for processing confirmation

### Step 2: Ask Questions
1. Go to "Query" page
2. Type your question in natural language
3. Examples:
   - "What are the main topics discussed?"
   - "Which products cost less than $500?"
   - "How does AI improve development?"
4. Get AI-generated answers with source references

### Step 3: View Results
1. Check "Output" page for query history
2. Export results as JSON
3. Review source chunks for each answer

## 🛠️ API Endpoints

### Document Upload
```bash
# Upload PDF
curl -X POST "http://localhost:8000/upload/pdf" \
  -F "file=@document.pdf"

# Upload CSV
curl -X POST "http://localhost:8000/upload/csv" \
  -F "file=@data.csv"
```

### Query System
```bash
# Ask question
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'
```

### Health Check
```bash
# Check system status
curl http://localhost:8000/health
```

## 📁 Project Structure

```
task1b-rag-system/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── uploads/              # Uploaded files directory
├── README.md             # This file
└── sample_data.csv       # Sample data for testing
```

## 🔍 Technical Details

### Models Used
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
  - Size: ~23MB
  - Purpose: Generate semantic embeddings for text chunks
  - Performance: Fast inference, good semantic understanding

- **Language Model**: `google/flan-t5-small`
  - Size: ~77MB
  - Purpose: Generate answers based on retrieved context
  - Features: Instruction-following, text-to-text generation

### Vector Search
- **FAISS**: Facebook AI Similarity Search
- **Index Type**: Flat L2 (exact search)
- **Similarity**: Cosine similarity for semantic matching
- **Top-K**: Retrieves 3 most relevant chunks per query

### Performance Optimizations
- GPU support (if available) for faster inference
- Efficient chunking strategy for better retrieval
- Memory-efficient vector storage
- Async file handling for better responsiveness

## 🧪 Testing the System

### Sample Queries for PDF Content
```
"What are the main challenges in AI development?"
"How can machine learning improve software engineering?"
"What tools are recommended for data processing?"
```

### Sample Queries for CSV Data
```
"What products are available in the electronics category?"
"Which items have the highest ratings?"
"Show me products released in 2024"
```

### Expected Behavior
1. **Relevant Answers**: AI provides contextual responses based on uploaded content
2. **Source Attribution**: Shows which document chunks were used for answers
3. **Graceful Degradation**: Handles queries when no relevant content is found
4. **Error Recovery**: Manages file upload errors and processing failures

## 🏋️ Performance Characteristics

- **Document Processing**: ~1-2 seconds per MB of content
- **Query Response**: ~2-5 seconds depending on LLM inference
- **Memory Usage**: ~500MB-1GB depending on loaded models
- **Concurrent Users**: Supports multiple users (FastAPI async)

## 🔧 Configuration Options

### Environment Variables
```bash
# Optional: Force CPU usage
export CUDA_VISIBLE_DEVICES=""

# Optional: Increase timeout for large files
export UPLOAD_TIMEOUT=300
```

### Model Selection
You can modify `app.py` to use different models:
```python
# For better quality (larger models)
embedding_model = SentenceTransformer('all-mpnet-base-v2')
llm = pipeline("text2text-generation", model="google/flan-t5-base")

# For faster inference (smaller models)
embedding_model = SentenceTransformer('all-MiniLM-L12-v2')
llm = pipeline("text2text-generation", model="google/flan-t5-small")
```

## 🚨 Troubleshooting

### Common Issues

1. **Model Download Fails**
   ```bash
   # Pre-download models
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

2. **Memory Issues**
   ```bash
   # Use CPU-only mode
   export CUDA_VISIBLE_DEVICES=""
   ```

3. **File Upload Errors**
   - Check file format (PDF/CSV only)
   - Ensure file size < 100MB
   - Verify file is not corrupted

4. **Poor Answer Quality**
   - Upload more relevant documents
   - Try more specific questions
   - Check if documents were processed successfully

## 🔮 Future Enhancements

- **Multi-document Queries**: Cross-reference multiple documents
- **Conversation Memory**: Remember previous questions in session
- **Advanced Chunking**: Smarter text segmentation strategies
- **Model Fine-tuning**: Domain-specific model adaptation
- **Real-time Updates**: Live document processing without restart

## 📊 Metrics & Monitoring

The system provides basic health metrics:
- Number of loaded document chunks
- System status and readiness
- Query processing time (visible in browser)
- Error rates (logged to console)

## 🎥 Demo Video

The demo video shows:
1. Starting the system with Docker
2. Uploading sample PDF and CSV files
3. Asking various questions
4. Reviewing answers and source information
5. Checking system health and query history

## 📝 Notes

- This is a minimal POC focused on core RAG functionality
- Models are intentionally small for fast startup and reasonable resource usage
- Web interface exceeds requirements but provides better demonstration of capabilities
- All code follows FastAPI best practices with proper error handling