# AI Research & Decision Intelligence Platform

An AI-powered research platform that combines Retrieval-Augmented Generation (RAG), multi-agent orchestration, and data analysis to transform unstructured documents and tabular datasets into structured, evidence-based insights.

The platform is designed to help users analyze documents, conduct research, explore datasets, and generate answers grounded in retrieved evidence.

## 🚀 Overview

### Problem Statement

Traditional research often requires users to manually review multiple PDF reports, spreadsheets, and other documents to extract relevant information and identify meaningful insights. This process can be time-consuming, repetitive, and difficult to verify.

The AI Research & Decision Intelligence Platform aims to streamline this workflow by combining document retrieval, AI-powered research, and quantitative data analysis in a unified application.

### Key Objectives

- Automate document ingestion and information retrieval.
- Enable semantic search across uploaded documents.
- Support quantitative analysis of CSV and Excel datasets.
- Coordinate specialized AI agents to handle different research tasks.
- Generate structured responses with source references to improve traceability.

## ✨ Key Features

- **Document Intelligence:** Load and process PDF documents for downstream retrieval and analysis.
- **Retrieval-Augmented Generation (RAG):** Retrieve semantically relevant document chunks to provide contextual information for LLM-generated answers.
- **Multi-Agent Orchestration:** Organize research, document analysis, and data analysis into specialized tasks.
- **Tabular Data Analysis:** Use Pandas to process structured datasets and calculate relevant metrics.
- **Evidence-Based Responses:** Associate generated insights with retrieved source material to support verification.
- **Persistent Storage:** Use PostgreSQL on Supabase to store application data and support persistent workflows.
- **Interactive Interface:** Provide a Streamlit interface for user interaction with the research system.
- **Resilient API Integration:** Apply retry mechanisms with exponential backoff to handle supported transient failures and API rate limits.

## 🏗️ System Architecture

The platform follows a modular architecture that separates the user interface, backend application, AI orchestration, retrieval pipeline, and data persistence.

```text
                         USER
                           |
                           v
                  +------------------+
                  | Streamlit UI     |
                  +------------------+
                           |
                           v
                  +------------------+
                  | FastAPI Backend   |
                  +------------------+
                           |
                           v
                  +------------------+
                  | AI Orchestrator   |
                  +------------------+
                           |
              +------------+------------+
              |            |            |
              v            v            v
       +-------------+ +----------+ +-------------+
       | Research    | | Document | | Data        |
       | Agent       | | Agent    | | Analyst     |
       +-------------+ +----------+ +-------------+
              |            |            |
              +------------+------------+
                           |
                           v
                  +------------------+
                  | Evidence &       |
                  | Analysis Results |
                  +------------------+
                           |
                           v
                  +------------------+
                  | Response         |
                  | Generation       |
                  +------------------+
                           |
                           v
                  +------------------+
                  | Final Answer     |
                  | with References  |
                  +------------------+

       Supporting Infrastructure:
       - Supabase PostgreSQL
       - pgvector
       - Google Gemini API
```

### Research Workflow

1. **Query Understanding:** Interpret the user's request and identify the required research or analysis tasks.
2. **Task Routing:** Route supported tasks to the appropriate agent or processing component.
3. **Information Retrieval:** Retrieve relevant document chunks using vector similarity search when document context is required.
4. **Data Processing:** Analyze supported CSV or Excel datasets using Pandas.
5. **Evidence Collection:** Gather retrieved passages and analytical results relevant to the request.
6. **Response Generation:** Use the available context to produce a structured answer with source references where supported.

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Frontend Interface | Streamlit |
| AI & LLM | LangChain, Google Gemini API |
| Embeddings | Google Gemini embedding model |
| Database | PostgreSQL, Supabase |
| Vector Search | pgvector |
| ORM | SQLAlchemy |
| Data Processing | Pandas |
| Document Processing | PyPDFLoader |
| Text Splitting | RecursiveCharacterTextSplitter |
| Configuration | Python dotenv |
| API Server | Uvicorn |

## 📁 Project Structure

```text
ai-research-decision-platform/
│
├── backend/
│   └── app/
│       ├── agents/
│       │   ├── orchestrator.py
│       │   └── ...
│       ├── rag/
│       │   └── ...
│       ├── database/
│       │   └── ...
│       ├── models.py
│       └── main.py
│
├── data/
│   └── ...
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

> Note: The structure above illustrates the intended organization. Update filenames and directories to match the actual repository. Do not include virtual environments, API keys, or sensitive configuration files in version control.

## ⚙️ Core Implementation

### 1. Document Ingestion & RAG Pipeline

The document processing pipeline prepares PDF content for semantic retrieval.

- Load PDF documents using PyPDFLoader.
- Split extracted text into smaller chunks using RecursiveCharacterTextSplitter.
- Generate vector embeddings for document chunks.
- Store embeddings and associated metadata in PostgreSQL using pgvector.
- Retrieve relevant chunks through similarity search to provide context for answer generation.

This approach allows the system to retrieve information from a document collection without requiring the entire collection to fit into the LLM context window.

### 2. Multi-Agent Task Orchestration

The application separates research and analysis responsibilities into specialized components.

- Interpret incoming requests.
- Identify the type of task required.
- Route supported tasks to the corresponding processing component.
- Collect results for downstream response generation.

The modular design makes it easier to maintain individual components and extend the platform with additional capabilities.

### 3. Tabular Data Analysis

The data analysis component uses Pandas to work with structured datasets.

Supported processing tasks may include:

- Loading CSV and Excel files.
- Inspecting columns, data types, and missing values.
- Filtering and aggregating records.
- Calculating descriptive statistics and summary metrics.
- Producing data-driven results for user queries.

The actual supported operations depend on the implemented data analysis logic.

### 4. Database Integration

Supabase provides a managed PostgreSQL database for application persistence and vector storage.

SQLAlchemy is used as the ORM layer for database interaction, while pgvector supports vector-based similarity search.

Depending on the implemented schema, the database may store document metadata, embeddings, conversation history, or other application records.

### 5. Error Handling & Reliability

The application incorporates retry mechanisms with exponential backoff for supported transient failures.

A typical retry strategy increases the delay between consecutive attempts to reduce repeated requests during temporary service interruptions.

Production-oriented improvements include:

- Explicit request timeouts.
- API error classification.
- Retry limits and backoff caps.
- Structured logging.
- Input validation.
- Graceful handling of unavailable external services.

## 💻 Getting Started

### Prerequisites

Ensure that the following are installed:

- Python 3.10 or another version supported by the project's dependencies.
- Git.
- A Supabase project with the required database configuration.
- A Google Gemini API key.
- Access to the required external APIs.

### 1. Clone the Repository

```bash
git clone https://github.com/tienbinh4060/ai-research-decision-platform.git
cd ai-research-decision-platform
```

### 2. Create a Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory based on `.env.example`.

Example configuration:

```ini
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_api_key
GOOGLE_API_KEY=your_google_gemini_api_key
```

Replace the placeholder values with your own credentials.

**Security note:** Never commit your actual `.env` file, API keys, or database credentials to GitHub. Use `.gitignore` to exclude sensitive files.

### 5. Start the Backend

From the project root, activate the virtual environment and run:

```bash
uvicorn app.main:app --app-dir backend --reload
```

If the backend uses a different import structure, adjust the command to match the actual application entry point.

Once the server starts, open the FastAPI documentation at:

`http://127.0.0.1:8000/docs`

### 6. Start the Frontend

Open a separate terminal, activate the virtual environment, and run:

```bash
streamlit run app.py
```

Streamlit will display the local URL where the application is available.

## 🔐 Security Considerations

- Store credentials in environment variables rather than source code.
- Exclude `.env`, virtual environments, and local datasets containing sensitive information from Git.
- Validate uploaded files and enforce reasonable file size limits.
- Apply appropriate authentication and authorization before exposing the application publicly.
- Restrict database permissions to the minimum required by the application.
- Avoid executing arbitrary code generated from user input or LLM responses.
- Treat retrieved documents and external content as untrusted input.

## ⚠️ Limitations

- Generated answers may contain inaccurate information if retrieved evidence is incomplete or irrelevant.
- Citation quality depends on the retrieval pipeline and the way source metadata is preserved.
- Vector similarity does not guarantee factual correctness.
- Data analysis capabilities depend on supported file formats and implemented operations.
- External LLM and embedding services may introduce latency, usage limits, and additional costs.
- Results should be reviewed before being used in high-impact decisions.

## 🔮 Future Improvements

Potential directions for further development include:

- Adding automated evaluation for retrieval quality and answer faithfulness.
- Improving citation verification and evidence attribution.
- Introducing document-level access control and user authentication.
- Supporting additional document formats and more advanced table extraction.
- Adding unit tests, integration tests, and end-to-end testing.
- Implementing observability with structured logs and performance metrics.
- Optimizing vector search using appropriate indexing and query strategies.
- Deploying the application with a production-ready configuration and CI/CD pipeline.

## 👨‍💻 Author

**Nguyen Tien Binh**

GitHub: [@tienbinh4060](https://github.com/tienbinh4060)

---

*This project explores the integration of LLMs, retrieval-augmented generation, multi-agent workflows, and structured data analysis in an extensible research platform.*
