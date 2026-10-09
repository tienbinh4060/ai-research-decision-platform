import pandas as pd
import os
import time
import io
import sys
from app.rag.engine import llm

def analyze_tabular_data(file_path: str, question: str) -> str:
    """
    Data Analyst Agent: Tự động phân tích cấu trúc, lọc bỏ tiêu đề rác 
    và thực thi code Python/Pandas để trả về kết quả số liệu chính xác tuyệt đối.
    """
    if not os.path.exists(file_path):
        return "Không tìm thấy file dữ liệu để phân tích."
    
    # 1. Đọc file linh hoạt
    lower_path = file_path.lower()
    try:
        if lower_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif lower_path.endswith('.xlsx') or lower_path.endswith('.xls'):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            df = pd.read_csv(file_path)
    except Exception as e:
        return f"❌ Lỗi đọc file: {str(e)}"
        
    # 2. Cung cấp cấu trúc tổng quan cho LLM để nó viết code Pandas xử lý
    summary_info = f"""
    - Tên file: {os.path.basename(file_path)}
    - Tổng số dòng: {len(df)}
    - Tên các cột (Columns): {list(df.columns)}
    - 10 dòng đầu tiên của DataFrame:
    {df.head(10).to_string()}
    """
    
    # 3. Yêu cầu LLM viết một đoạn mã Python ngắn gọn để trả lời câu hỏi
    prompt = f"""Bạn là một lập trình viên Python và Chuyên gia Pandas xuất sắc.
    Dưới đây là thông tin về một DataFrame tên là `df`:
    {summary_info}
    
    CÂU HỎI CỦA NGƯỜI DÙNG: {question}
    
    Nhiệm vụ: Hãy viết một đoạn code Python (sử dụng biến `df` đã có sẵn) để tính toán hoặc tìm ra kết quả chính xác cho câu hỏi trên. 
    QUAN TRỌNG: 
    - Đoạn code phải tự xử lý việc bỏ qua các dòng tiêu đề rác ở đầu (nếu có), ép kiểu cột số liệu sang dạng numeric bằng `pd.to_numeric(..., errors='coerce')`.
    - In kết quả ra màn hình bằng lệnh `print(...)`.
    - CHỈ TRẢ VỀ ĐOẠN CODE PYTHON THUẦN TÚY nằm trong cặp định dạng ```python ... ```, không giải thích thêm gì bên ngoài.
    """
    
    # Gọi LLM lấy đoạn code có tích hợp retry chống lỗi quá tải/timeout (503/504)
    code_text = ""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = llm.invoke(prompt)
            code_text = response.content
            break
        except Exception as e:
            if ("503" in str(e) or "504" in str(e)) and attempt < max_attempts - 1:
                time.sleep(3)
            else:
                raise e
    
    # Ép kiểu an toàn chống lỗi list cho code_text
    if isinstance(code_text, list):
        code_text = "".join([str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in code_text])
    else:
        code_text = str(code_text)

    # Trích xuất code từ Markdown block (```python ... ```)
    import re
    code_match = re.search(r"```python\s*(.*?)\s*```", code_text, re.DOTALL)
    if code_match:
        python_code = code_match.group(1)
    else:
        python_code = code_text.replace("```python", "").replace("```", "").strip()

    # 4. Thực thi an toàn đoạn code Python vừa sinh ra trên DataFrame thực tế
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    execution_success = True
    error_message = ""
    
    try:
        local_vars = {"df": df, "pd": pd}
        exec(python_code, {}, local_vars)
        output_result = new_stdout.getvalue()
    except Exception as e:
        execution_success = False
        error_message = str(e)
        output_result = ""
    finally:
        sys.stdout = old_stdout
        
    # 5. Nếu code chạy thành công, đưa kết quả thô qua LLM để viết báo cáo hoàn chỉnh
    if execution_success and output_result.strip():
        final_prompt = f"""Dựa vào kết quả thực thi mã nguồn Python từ dữ liệu của người dùng:
        CÂU HỎI: {question}
        KẾT QUẢ TÍNH TOÁN THỰC TẾ:
        {output_result}
        
        Hãy viết câu trả lời bằng tiếng Việt một cách rõ ràng, lịch sự, nêu rõ STT, Họ tên và số liệu chính xác nhất cho người dùng. Không kèm theo bất kỳ siêu dữ liệu hay mã phụ nào.
        """
        
        final_response_content = ""
        for attempt in range(max_attempts):
            try:
                final_res = llm.invoke(final_prompt)
                final_response_content = final_res.content
                break
            except Exception as e:
                if ("503" in str(e) or "504" in str(e)) and attempt < max_attempts - 1:
                    time.sleep(3)
                else:
                    raise e
        
        if isinstance(final_response_content, list):
            clean_text = "".join([str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in final_response_content])
            return clean_text.strip()
        
        return str(final_response_content).strip()
    else:
        return f"⚠️ Agent đã thử viết mã phân tích nhưng gặp lỗi thực thi: {error_message}"