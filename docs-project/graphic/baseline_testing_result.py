import matplotlib.pyplot as plt
import numpy as np

users = [50, 100, 150, 200, 250]
avg_response = [36307, 54252, 82041, 110146, 133626]
p90_response = [101082, 101000, 152496, 207790, 275362]

plt.figure(figsize=(12, 7))

# Plotting Data
# Garis untuk Average
plt.plot(users, avg_response, marker='o', linestyle='-', color='#1f77b4', linewidth=2, label='Average Response Time')
# Garis untuk P90 (Putus-putus untuk membedakan)
plt.plot(users, p90_response, marker='s', linestyle='--', color='#d62728', linewidth=2, label='90% Line (P90)')

# Menambahkan Judul dan Label
plt.title('Perbandingan Average Response Time vs 90% Line (Baseline) Semakin Rendah = Baik', fontsize=14, fontweight='bold')
plt.xlabel('Jumlah Virtual Users', fontsize=12)
plt.ylabel('Waktu Respon (ms)', fontsize=12)

# Mengisi area di antara garis untuk menunjukkan "Gap" latency
plt.fill_between(users, avg_response, p90_response, color='#d62728', alpha=0.1, label='Latency Gap')

# Menambahkan Grid
plt.grid(True, linestyle=':', alpha=0.6)

# Menambahkan Legend
plt.legend(fontsize=11)

# Menampilkan nilai di titik data terakhir (untuk 250 users) agar tidak terlalu penuh
plt.annotate(f"{avg_response[-1]} ms", (users[-1], avg_response[-1]), textcoords="offset points", xytext=(0,-15), ha='center', color='#1f77b4', fontweight='bold')
plt.annotate(f"{p90_response[-1]} ms", (users[-1], p90_response[-1]), textcoords="offset points", xytext=(0,10), ha='center', color='#d62728', fontweight='bold')

# Menampilkan Grafik
plt.tight_layout()
plt.show()