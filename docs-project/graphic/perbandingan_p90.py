import matplotlib.pyplot as plt
import numpy as np

users = ['50', '100', '150', '200', '250']
base_p90 = [101082, 101000, 152496, 207790, 275362]
opt_p90 = [461, 445, 472, 19507, 31150]

x = np.arange(len(users))
width = 0.35

plt.figure(figsize=(10, 6))
bar1 = plt.bar(x - width/2, base_p90, width, label='Baseline', color='#ff7f0e') # Oranye
bar2 = plt.bar(x + width/2, opt_p90, width, label='Pasca-Optimasi', color='#1f77b4') # Biru

plt.ylabel('P90 Response Time (ms)')
plt.title('Perbandingan P90 / Stabilitas (Semakin Rendah = Baik)', fontweight='bold')
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