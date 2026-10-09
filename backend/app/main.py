import os
import shutil
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import cấu hình DB
from app.database import engine, get_db, Base
from app.models import ChatHistory

# Import các hàm AI
from app.rag.engine import ingest_pdf
from app.agents.orchestrator import run_research_agent
from app.agents.data_agent import analyze_tabular_data

# Khởi tạo bảng trong Supabase nếu chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Research & Decision Intelligence Platform")

class Message(BaseModel):
    role: str
    content: str

class QuestionRequest(BaseModel):
    question: str
    history: list[Message] = []

@app.get("/")
def read_root():
    return {"status": "online", "message": "Hệ thống Multi-Agent AI đã sẵn sàng!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint upload file tài liệu PDF hoặc dữ liệu bảng (CSV/Excel)"""
    try:
        # 1. Đảm bảo thư mục 'data' tồn tại
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", file.filename)
        
        # 2. Lưu file từ web xuống thư mục 'data' local
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 3. Phân luồng xử lý: Nếu là PDF thì băm dữ liệu (RAG)
        if file.filename.lower().endswith(".pdf"):
            ingest_pdf(file_path, file.filename)
            return {"message": f"✅ Đã nạp và băm dữ liệu từ file PDF: {file.filename}"}
        
        # Nếu là CSV/Excel thì chỉ cần lưu lại để Data Agent tự đọc
        elif file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
            return {"message": f"✅ Đã tải lên dữ liệu bảng: {file.filename}"}
            
        else:
            return {"message": f"✅ Đã lưu file: {file.filename}"}
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Lỗi upload: {str(e)}"})

@app.post("/ask")
def ask_question(request: QuestionRequest, db: Session = Depends(get_db)):
    """Endpoint hỏi đáp RAG có lưu lịch sử"""
    # 1. Lưu câu hỏi user vào DB
    user_msg = ChatHistory(role="user", content=request.question)
    db.add(user_msg)
    db.commit()

    try:
        # 2. Gọi RAG Agent xử lý
        result = run_research_agent(request.question, request.history)
        answer = result["answer"]
        sources = result["sources"]
        
        # 3. Lưu câu trả lời bot vào DB
        bot_msg = ChatHistory(role="assistant", content=answer)
        db.add(bot_msg)
        db.commit()

        return {
            "question": request.question,
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/history")
def get_chat_history(db: Session = Depends(get_db)):
    """Endpoint lấy toàn bộ lịch sử chat để hiển thị lên UI"""
    messages = db.query(ChatHistory).order_by(ChatHistory.created_at.asc()).limit(50).all()
    history = [{"role": msg.role, "content": msg.content} for msg in messages]
    return {"history": history}