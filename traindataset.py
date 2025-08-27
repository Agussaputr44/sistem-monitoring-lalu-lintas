from ultralytics import YOLO
model_yolo = YOLO("yolov8n.pt")
model_yolo.train(
    data="data.yaml",      # arahkan ke file data.yaml kamu
    epochs=100,             # jumlah epoch training
    imgsz=640,             # ukuran input image
    batch=8,               # batch size, sesuaikan dengan RAM/GPU
    project="runs/train",  # folder output
    name="kendaraan",      # nama eksperimen
    exist_ok=True          # overwrite kalau sebelumnya sudah ada
)