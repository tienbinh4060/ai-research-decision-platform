import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# 1. Định vị chính xác file .env
# Lấy đường dẫn của thư mục hiện tại (backend/app)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Lùi lại 2 cấp (../..) để ra thư mục gốc chứa file .env
env_path = os.path.abspath(os.path.join(current_dir, "../../.env"))

# 2. Tải biến môi trường
load_dotenv(dotenv_path=env_path)

# 3. Lấy link Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Đề phòng trường hợp lỗi không tìm thấy link
if not DATABASE_URL:
    raise ValueError(f"Không tìm thấy DATABASE_URL! Đang tìm file .env tại: {env_path}")

# Đổi postgres:// thành postgresql:// theo chuẩn SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 4. Khởi tạo DB
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()