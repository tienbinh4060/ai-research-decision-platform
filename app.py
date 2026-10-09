import streamlit as st
import requests

# 1. Cấu hình trang web
st.set_page_config(page_title="AI Research Platform", page_icon="🤖", layout="wide")

# 2. KHU VỰC TẢI TÀI LIỆU (SIDEBAR BÊN TRÁI)
with st.sidebar:
    st.header("📂 Nạp tài liệu & Dữ liệu")
    uploaded_file = st.file_uploader("Kéo thả file (PDF, CSV, Excel)", type=["pdf", "csv", "xlsx", "xls"])
    
    if "processed_file" not in st.session_state:
        st.session_state.processed_file = None

    if uploaded_file is not None and uploaded_file.name != st.session_state.processed_file:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        with st.spinner(f"🚀 Đang tải và xử lý '{uploaded_file.name}' lên hệ thống..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                res = requests.post("http://127.0.0.1:8000/upload", files=files, timeout=180)
                data = res.json() # Đọc dữ liệu JSON trả về
                
                # Nếu Backend trả về 200 OK và KHÔNG có key "error" bên trong
                if res.status_code == 200 and "error" not in data:
                    st.success(data.get("message", "Tải file thành công!"))
                    st.session_state.processed_file = uploaded_file.name
                    st.session_state.file_type = file_extension
                    st.session_state.messages = [
                        {"role": "assistant", "content": f"Đã chuyển sang nghiên cứu tài liệu **{uploaded_file.name}**! Tôi đã sẵn sàng, bạn muốn hỏi gì?"}
                    ]
                    st.rerun()
                else:
                    # Hiển thị chính xác lỗi mà Backend đang gặp phải
                    error_msg = data.get('error', 'Lỗi không xác định từ máy chủ')
                    st.error(f"❌ Backend báo lỗi khi xử lý PDF: {error_msg}")
                    
            except Exception as e:
                st.error(f"Lỗi kết nối Backend: {str(e)}")

# Đảm bảo session lưu loại file
if "file_type" not in st.session_state:
    st.session_state.file_type = "pdf"

# 3. KHU VỰC CHAT CHÍNH
st.title("🤖 AI Research & Decision Intelligence Platform")
st.caption("Hệ thống Multi-Agent RAG tích hợp Document Agent & Data Analyst Agent")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Chào bạn! Hãy kéo thả file tài liệu (PDF) hoặc bảng số liệu (CSV/Excel) vào thanh bên trái để bắt đầu."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 Xem trích dẫn từ tài liệu gốc"):
                for idx, source in enumerate(message["sources"]):
                    st.info(f"**Trích đoạn {idx+1}:** {source}")

# 4. KHUNG NHẬP CÂU HỎI
if prompt := st.chat_input("Nhập câu hỏi hoặc yêu cầu phân tích tại đây...", key="user_chat_input"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Đang phân tích yêu cầu và xử lý... ⏳")
        
        try:
            # KIỂM TRA LUỒNG XỬ LÝ: Nếu là file dữ liệu bảng (CSV/Excel) -> Gọi Data Analyst Agent
            if st.session_state.file_type in ["csv", "xlsx", "xls"]:
                if not st.session_state.processed_file:
                    message_placeholder.error("⚠️ Vui lòng tải lên một file dữ liệu trước khi đặt câu hỏi!")
                else:
                    payload = {
                        "file_name": st.session_state.processed_file,
                        "question": prompt
                    }
                    response = requests.post("http://127.0.0.1:8000/analyze-data", data=payload, timeout=180)
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("analysis", "")
                        message_placeholder.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": []})
                    else:
                        message_placeholder.error(f"❌ Lỗi từ Data Analyst Agent: {response.status_code}")
            
            # NẾU LÀ FILE VĂN BẢN (PDF) -> Gọi RAG Engine / Orchestrator Agent cũ
            else:
                payload = {
                    "question": prompt,
                    "history": st.session_state.messages[:-1]
                }
                response = requests.post("http://127.0.0.1:8000/ask", json=payload, timeout=180)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")
                    sources = data.get("sources", [])
                    
                    message_placeholder.markdown(answer)
                    
                    if sources:
                        with st.expander("📚 Xem trích dẫn từ tài liệu gốc"):
                            for idx, source in enumerate(sources):
                                st.info(f"**Trích đoạn {idx+1}:** {source}")
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                else:
                    message_placeholder.error(f"❌ Backend trả về lỗi: {response.status_code}")
                    
        except Exception as e:
            message_placeholder.error(f"❌ Không thể kết nối với Backend. Chi tiết: {str(e)}")