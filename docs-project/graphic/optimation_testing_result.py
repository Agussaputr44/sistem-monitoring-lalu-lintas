import matplotlib.pyplot as plt

# Data dari Tabel Rekapitulasi Pasca-Optimasi
users = [50, 100, 150, 200, 250]
avg_response = [192, 172, 192, 6905, 14220]
p90_response = [461, 445, 472, 19507, 31150]

# Pengaturan Ukuran Grafik
plt.figure(figsize=(10, 6))

# Plotting Data
# Garis P90 (Orange)
plt.plot(users, p90_response, marker='s', linestyle='--', color='#ff7f0e', linewidth=2, label='90% Line (P90)')
# Garis Average (Hijau - Menandakan Sukses)
plt.plot(users, avg_response, marker='o', linestyle='-', color='#2ca02c', linewidth=2.5, label='Average Response Time')

# Judul dan Label
plt.title('Perbandingan Average Response Time vs 90% Line (Pasca-Optimasi)', fontsize=14, fontweight='bold')
plt.xlabel('Jumlah Virtual Users', fontsize=12)
plt.ylabel('Waktu Respon (ms)', fontsize=12)

# Grid dan Legend
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()

# Anotasi Nilai Average agar mudah dibaca
for i, txt in enumerate(avg_response):
    plt.annotate(f"{txt}", (users[i], avg_response[i]), 
                 textcoords="offset points", xytext=(0,10), ha='center', color='#2ca02c', fontweight='bold')

plt.tight_layout()
plt.show()