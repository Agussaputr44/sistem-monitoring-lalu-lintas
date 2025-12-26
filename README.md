# Sistem Monitoring Lalu Lintas (Bengkalis Traffic Intelligence)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![YOLOv8](https://img.shields.io/badge/YOLOv8-FF2D20?style=for-the-badge&logo=ultralytics)
![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

## 📌 Deskripsi Proyek
**Bengkalis Traffic Intelligence** adalah sistem pemantauan arus lalu lintas cerdas yang mengintegrasikan *Computer Vision* dengan *Real-time Dashboard*. Menggunakan model **YOLOv8**, sistem ini mampu mendeteksi kendaraan dari berbagai sumber video, menghitung volume kendaraan, serta memperkirakan kecepatan untuk kebutuhan analisis data lalu lintas secara otomatis.

## ✨ Fitur Utama
- **Deteksi & Klasifikasi Kendaraan**: Mendeteksi mobil, motor, bus, truk, hingga pickup dengan akurasi tinggi.
- **Estimasi Kecepatan**: Menghitung perkiraan kecepatan kendaraan dalam km/jam menggunakan analisis perspektif.
- **Vehicle Tracking**: Memberikan ID unik pada setiap objek untuk melacak pergerakan dan menghindari perhitungan ganda.
- **Live Stream**: Menyediakan aliran video MJPEG melalui endpoint API untuk pemantauan langsung.
- **Dashboard Statistik**: Visualisasi data arus lalu lintas menggunakan grafik interaktif berbasis Flutter.

## 🛠️ Teknologi yang Digunakan
- **Backend**: FastAPI (Python).
- **AI/ML**: YOLOv8 (Ultralytics) & OpenCV.
- **Database**: MySQL & Redis (untuk caching/optimasi).
- **Frontend**: Flutter dengan manajemen state BLoC.
- **Infrastruktur**: Docker & Docker Compose.

## 📋 Prasyarat & Instalasi
1. **Clone Repo**: `git clone https://github.com/Agussaputr44/sistem-monitoring-lalu-lintas.git`
2. **Backend**: Masuk ke folder `BE/` dan jalankan `docker-compose up --build`.
3. **Frontend**: Masuk ke folder `FE/dashboard_app/` dan jalankan `flutter run`.

## 🚀 Penggunaan
- **API Root**: `http://localhost:8000/`.
- **Video Feed**: `http://localhost:8001/video_feed`.

## 📄 Lisensi
Proyek ini dilisensikan di bawah **MIT License**.

---
**(https://github.com/Agussaputr44)**