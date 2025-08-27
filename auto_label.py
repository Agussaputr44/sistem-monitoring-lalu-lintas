from ultralytics import YOLO
import os

# 1. Load model COCO pretrained (sudah ada truck & motorcycle)
model = YOLO("yolov8n.pt")

# 2. Folder tempat gambar
image_folder = "datasets/kendaraan_bengkalis/images"

# 3. Jalankan prediksi + simpan label YOLO format
results = model.predict(
    source=image_folder,   # folder gambar
    save_txt=True,         # simpan label ke txt
    save_conf=True,        # simpan confidence juga
    project="datasets/kendaraan_bengkalis", # hasil disimpan ke sini
    name="labels_auto"     # nama folder hasil
)

print("✅ Auto-label selesai! Cek folder datasets/my100/labels_auto/labels")
