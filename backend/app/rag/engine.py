import os
import time
from dotenv import load_dotenv, find_dotenv

from supabase import create_client, Client
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

load_dotenv(find_dotenv())

# 1. Kết nối Supabase
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# 2. Embedding & Vector Store
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vector_store = SupabaseVectorStore(
    client=supabase,
    embedding=embeddings, 
    table_name="documents",
    query_name="match_documents",
)

# 3. LLM (Não bộ)
llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash", 
    temperature=0.3, 
    max_retries=5,
    request_timeout=60
)

def search_documents(query: str, k: int = 10):
    """Hàm thực hiện tìm kiếm tương đồng trên Supabase"""
    docs = vector_store.similarity_search(query, k=k)
    return docs

def ingest_pdf(file_path: str, filename: str = ""):
    """Hàm xử lý băm file và đẩy lên Supabase có bắt lỗi chi tiết"""
    if not filename:
        filename = os.path.basename(file_path)
        
    print(f"📄 Đang tiến hành đọc file PDF: {file_path}")
    
    try:
        # Đọc file PDF
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        # Chia nhỏ văn bản
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(docs)
        print(f"✂️ Đã chia nhỏ thành {len(chunks)} đoạn văn bản.")
        
        # Đẩy lên Supabase Vector Store với cơ chế thử lại
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                vector_store.add_documents(chunks)
                print("🚀 Đã đẩy vector thành công lên Supabase!")
                break
            except Exception as e:
                if "503" in str(e) and attempt < max_attempts - 1:
                    print(f"⚠️ Google Embedding đang quá tải (503), đang thử lại lần {attempt + 2}...")
                    time.sleep(3)
                else:
                    raise e
                    
        return len(chunks)
        
    except Exception as e:
        print(f"❌ LỖI NGHIÊM TRỌNG TRONG HÀM INGEST_PDF: {str(e)}")
        raise e