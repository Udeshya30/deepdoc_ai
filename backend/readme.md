backend/
├── main.py                  # FastAPI entry point
├── models/                  
│   └── mistral_runner.py    # Load and use Mistral LLM
├── services/
│   ├── file_parser.py       # PDF/DOCX text extraction
│   ├── rag_engine.py        # Embedding, vector search, Q&A
│   └── summarizer.py        # Summarize chunks
├── routes/
│   ├── upload.py            # /upload endpoint
│   ├── ask.py               # /ask endpoint
│   ├── summary.py           # /summary endpoint
│   └── translate.py         # (Optional)
├── data/
│   ├── uploads/             # Uploaded files
│   └── chroma_db/           # Vector DB storage
└── requirements.txt
