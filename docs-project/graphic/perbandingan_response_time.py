import matplotlib.pyplot as plt
import numpy as np

users = ['50', '100', '150', '200', '250']
base_avg = [36307, 54252, 82041, 110146, 133626]
opt_avg = [192, 172, 192, 6905, 14220]

x = np.arange(len(users))
width = 0.35

plt.figure(figsize=(10, 6))
bar1 = plt.bar(x - width/2, base_avg, width, label='Baseline', color='#d62728') # Merah
bar2 = plt.bar(x + width/2, opt_avg, width, label='Pasca-Optimasi', color='#2ca02c') # Hijau

plt.ylabel('Average Response Time (ms)')
plt.title('Perbandingan Average Response Time (Semakin Rendah = Baik)', fontweight='bold')
plt.xticks(x, users)
plt.xlabel('Jumlah Users (Virtual)')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)

for rect in bar1 + bar2:
    height = rect.get_height()
    plt.annotate(f'{int(height)}', xy=(rect.get_x() + rect.get_width() / 2, height),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()