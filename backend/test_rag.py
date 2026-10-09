import os
from dotenv import load_dotenv, find_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector

# 1. Tải biến môi trường
load_dotenv(find_dotenv())

# 2. Xử lý đường link DB
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)

print("--- BẮT ĐẦU QUÁ TRÌNH RAG PIPELINE ---")
print("1. Đang kết nối Vector DB Supabase...")

# 3. Khởi tạo mô hình Embedding Mã nguồn mở (Local)
print("-> Đang tải mô hình HuggingFace (chỉ mất vài chục giây cho lần đầu tiên)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 4. Kết nối bảng Vector trên Supabase
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="research_docs",
    connection=db_url,
    use_jsonb=True,
)

def ingest_pdf(file_path: str):
    print(f"2. Đang đọc file PDF: {file_path}")
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    print("3. Đang băm nhỏ tài liệu (Chunking)...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    print(f"   -> Đã cắt thành {len(chunks)} đoạn văn bản nhỏ.")

    print("4. Đang mã hóa Embedding bằng sức mạnh CPU/GPU máy tính và tải lên Supabase...")
    vector_store.add_documents(chunks)
    print("✅ HOÀN TẤT! Dữ liệu đã nằm an toàn trên Vector DB Đám mây.")

if __name__ == "__main__":
    pdf_path = "data/sample_report.pdf"
    if os.path.exists(pdf_path):
        ingest_pdf(pdf_path)
    else:
        print(f"❌ Lỗi: Không tìm thấy file tại {pdf_path}")