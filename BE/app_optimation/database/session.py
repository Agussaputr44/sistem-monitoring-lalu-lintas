from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app_optimation.core.config import settings
from typing import Generator

# ============================================================
# === KONFIGURASI ENGINE DENGAN CONNECTION POOL TUNING =======
# ============================================================
# Tujuan: Mencegah error "QueuePool limit of size 5 overflow"
# saat Load Test dengan JMeter yang memiliki throughput tinggi.
# ============================================================

engine = create_engine(
    settings.DATABASE_URL,
    # 1. Cek kesehatan koneksi sebelum diberikan ke aplikasi
    pool_pre_ping=True,      
    
    # 2. Standby Connection (Jumlah loket yang buka terus)
    # Default: 5 -> Kita naikkan jadi 50 agar siap menerima traffic mendadak
    pool_size=50,            
    
    # 3. Emergency Connection (Jumlah loket tambahan dadakan)
    # Default: 10 -> Kita naikkan jadi 50.
    # Total koneksi maksimal yang bisa dibuat = pool_size + max_overflow = 100
    max_overflow=50,         
    
    # 4. Batas Waktu Antrean
    # Jika 100 koneksi terpakai semua, request ke-101 menunggu 30 detik sebelum error.
    pool_timeout=30,         
    
    # 5. Daur Ulang Koneksi
    # Koneksi akan diputus dan dibuat baru tiap 30 menit (1800 detik)
    # untuk mencegah masalah koneksi "stale" di MySQL.
    pool_recycle=1800        
)

# Membuat session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk model database
Base = declarative_base()

# ============================================================
# === DEPENDENCY INJECTION (WAJIB ADA) =======================
# ============================================================
def get_db() -> Generator:
    """
    Fungsi ini digunakan di setiap endpoint/controller FastAPI
    untuk mendapatkan sesi database dan menutupnya otomatis.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()