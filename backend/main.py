import os
import shutil
import time
from dotenv import load_dotenv, find_dotenv

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

# Import lõi AI và kết nối Database
from supabase import create_client, Client
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# ==========================================
# 1. TẢI MÔI TRƯỜNG & KẾT NỐI DATABASE
# ==========================================
load_dotenv(find_dotenv())

# Khởi tạo kết nối Supabase
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Cài đặt "Lõi nhúng" bằng siêu máy tính Google
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# Gắn kết nối vào Vector Store
vector_store = SupabaseVectorStore(
    client=supabase,
    embedding=embeddings, 
    table_name="documents",
    query_name="match_documents",
)

# ==========================================
# 2. KHỞI TẠO NÃO BỘ LLM
# ==========================================
llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash", 
    temperature=0.3, 
    max_retries=5,
    request_timeout=60
)

# ==========================================
# 3. KHỞI TẠO FASTAPI & CẤU TRÚC DỮ LIỆU
# ==========================================
app = FastAPI(title="AI Research Platform API")

class Message(BaseModel):
    role: str  # "user" hoặc "assistant"
    content: str

class QuestionRequest(BaseModel):
    question: str
    history: list[Message] = []  # Danh sách lịch sử tin nhắn

@app.get("/")
def read_root():
    return {"status": "online", "message": "Hệ thống AI đã sẵn sàng!"}

# ==========================================
# 4. API UPLOAD & TỰ ĐỘNG DỌN DẸP FILE CŨ
# ==========================================
@app.post("/upload")
def upload_and_ingest_pdf(file: UploadFile = File(...)):
    print(f"👉 1. Đã nhận được file: {file.filename}")
    os.makedirs("data", exist_ok=True)
    file_path = f"data/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Dọn dẹp dữ liệu cũ an toàn trong Supabase trước khi nạp file mới
    try:
        supabase.table("documents").delete().gte("id", 0).execute()
        print("🧹 Đã tự động dọn dẹp sạch sẽ cơ sở dữ liệu cũ.")
    except Exception as e:
        print(f"⚠️ Lỗi dọn dẹp DB cũ: {e}")

    print("👉 2. Bắt đầu băm nhỏ tài liệu mới...")
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    
    print(f"👉 3. Đã băm xong {len(chunks)} đoạn. Đang đẩy dữ liệu lên Supabase...")
    vector_store.add_documents(chunks) 
    
    print("👉 4. Tải lên THÀNH CÔNG!")
    return {
        "status": "success", 
        "message": f"Đã dọn dẹp, băm và nạp thành công {len(chunks)} đoạn từ '{file.filename}' lên Đám mây!"
    }

# ==========================================
# 5. API TRẢ LỜI CÂU HỎI (ASK)
# ==========================================
@app.post("/ask")
def ask_research_agent(request: QuestionRequest):
    docs = vector_store.similarity_search(request.question, k=10)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    chat_history_str = ""
    for msg in request.history:
        role_label = "Người dùng" if msg.role == "user" else "Trợ lý AI"
        chat_history_str += f"{role_label}: {msg.content}\n"
    
    prompt = f"""Bạn là một Chuyên gia Nghiên cứu và Phân tích Tài liệu cấp cao. 
    Nhiệm vụ của bạn là đọc kỹ tài liệu được cung cấp bên dưới, kết hợp với lịch sử trò chuyện để phân tích câu hỏi một cách **chi tiết, đầy đủ, có chiều sâu và logic**. 
    Không được trả lời hời hợt hoặc cắt xén thông tin nếu tài liệu có đề cập đến. Hãy giải thích rõ ràng các ý chính, cấu trúc và chi tiết bổ trợ có trong tài liệu.
    Nếu thông tin hoàn toàn không có trong tài liệu, hãy nói rõ: "Tôi không tìm thấy thông tin này trong tài liệu".
    
    LỊCH SỬ TRÒ CHUYỆN TRƯỚC ĐÓ:
    {chat_history_str}
    
    TÀI LIỆU CUNG CẤP ĐỂ THAM KHẢO:
    {context}
    
    CÂU HỎI MỚI CỦA NGƯỜI DÙNG: {request.question}
    """
    
    max_attempts = 3
    response = None
    for attempt in range(max_attempts):
        try:
            response = llm.invoke(prompt)
            break
        except Exception as e:
            if "503" in str(e) and attempt < max_attempts - 1:
                print(f"⚠️ Google đang quá tải (503), đang thử lại lần {attempt + 2}...")
                time.sleep(3)
            else:
                raise e
    
    final_answer = response.content
    if isinstance(final_answer, list):
        final_answer = final_answer[0].get("text", str(final_answer))
    
    return {
        "question": request.question,
        "answer": final_answer,
        "sources": [doc.page_content for doc in docs] 
    }