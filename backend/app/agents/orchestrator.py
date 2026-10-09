import time
from app.rag.engine import search_documents, llm

def run_research_agent(question: str, history: list) -> dict:
    """
    Orchestrator Agent: Tiếp nhận câu hỏi, lấy tài liệu qua RAG, 
    kết hợp lịch sử chat và gọi LLM phân tích sâu sắc.
    """
    # 1. Lấy ngữ cảnh từ Vector Store (RAG)
    docs = search_documents(question, k=10)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # 2. Xây dựng lịch sử trò chuyện
    chat_history_str = ""
    for msg in history:
        role_label = "Người dùng" if msg.role == "user" else "Trợ lý AI"
        chat_history_str += f"{role_label}: {msg.content}\n"
    
    # 3. Xây dựng Prompt chuyên gia
    prompt = f"""Bạn là một Chuyên gia Nghiên cứu và Phân tích Tài liệu cấp cao. 
    Nhiệm vụ của bạn là đọc kỹ tài liệu được cung cấp bên dưới, kết hợp với lịch sử trò chuyện để phân tích câu hỏi một cách **chi tiết, đầy đủ, có chiều sâu và logic**. 
    Không được trả lời hời hợt hoặc cắt xén thông tin nếu tài liệu có đề cập đến. Hãy giải thích rõ ràng các ý chính, cấu trúc và chi tiết bổ trợ có trong tài liệu.
    Nếu thông tin hoàn toàn không có trong tài liệu, hãy nói rõ: "Tôi không tìm thấy thông tin này trong tài liệu".
    
    LỊCH SỬ TRÒ CHUYỆN TRƯỚC ĐÓ:
    {chat_history_str}
    
    TÀI LIỆU CUNG CẤP ĐỂ THAM KHẢO:
    {context}
    
    CÂU HỎI MỚI CỦA NGƯỜI DÙNG: {question}
    """
    
    # 4. Gọi LLM với cơ chế chống lỗi quá tải (503)
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
        "answer": final_answer,
        "sources": [doc.page_content for doc in docs]
    }