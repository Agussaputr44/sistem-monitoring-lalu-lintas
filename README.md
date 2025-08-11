
```markdown
# 🚦 Sistem Monitoring Lalu Lintas dengan YOLO

<p align="center">
  <img src="https://raw.githubusercontent.com/ultralytics/assets/main/logo/yolo-logo.png" width="300" alt="YOLO Logo" />
</p>

Aplikasi ini adalah sistem **monitoring lalu lintas** yang menggunakan **YOLO (You Only Look Once)** untuk mendeteksi dan mengklasifikasikan kendaraan yang melintas di suatu jalan.  
Sistem ini menghitung **volume kendaraan secara real-time**, sehingga sangat bermanfaat untuk analisis kepadatan lalu lintas dan pengambilan keputusan manajemen lalu lintas.

---

## ✨ Fitur Utama
- 🔍 **Deteksi kendaraan** (mobil, motor, bus, truk, dll.)
- 🏷 **Klasifikasi jenis kendaraan**
- 📈 **Penghitungan volume kendaraan** dalam periode waktu tertentu
- 📊 **Visualisasi data lalu lintas**
- 🔗 **Integrasi API** untuk penyimpanan dan analisis lebih lanjut

---

## 📂 Struktur Folder
```

.
├── app/                  # Source code utama aplikasi
├── yolo/                 # Model YOLO dan script deteksi
├── docker-compose.yml    # Konfigurasi Docker
├── requirements.txt      # Dependensi Python
├── .env                  # Environment variables
├── flow app.excalidraw   # Diagram alur sistem
└── .gitignore

````

---

## 🚀 Instalasi & Menjalankan

### 1️⃣ Clone Repository
```bash
git clone https://github.com/username/monitoring-lalu-lintas.git
cd monitoring-lalu-lintas
````

### 2️⃣ Install Dependensi

Menggunakan **pip**:

```bash
pip install -r requirements.txt
```

Atau menggunakan **Docker**:

```bash
docker-compose up --build
```

### 3️⃣ Konfigurasi Environment

Buat file `.env`:

```
YOLO_MODEL_PATH=yolo/model.pt
CAMERA_SOURCE=0
API_URL=http://localhost:5000
```

### 4️⃣ Jalankan Aplikasi

```bash
python app/main.py
```

---

## 📊 Diagram Alur Sistem

File diagram tersedia di [`flow app.excalidraw`](./flow%20app.excalidraw).

---

## 🖼 Contoh Hasil Deteksi

<p align="center">
  <img src="https://raw.githubusercontent.com/ultralytics/yolov5/master/data/images/zidane.jpg" width="600" alt="Contoh Deteksi YOLO" />
</p>

---

## 🛠 Teknologi yang Digunakan

* [Python](https://www.python.org/)
* [YOLO](https://github.com/ultralytics/yolov5)
* [Docker](https://www.docker.com/)
* [Excalidraw](https://excalidraw.com/)

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

---

💡 *Dikembangkan bersama tim untuk sistem analisis lalu lintas berbasis AI.*

```


