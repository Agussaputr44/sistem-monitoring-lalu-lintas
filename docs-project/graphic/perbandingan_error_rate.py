import matplotlib.pyplot as plt
import numpy as np

users = ['50', '100', '150', '200', '250']
base_err = [18.00, 23.25, 29.00, 24.13, 23.40]
opt_err = [0.00, 0.00, 0.00, 0.00, 0.70]

x = np.arange(len(users))
width = 0.35

plt.figure(figsize=(10, 6))
bar1 = plt.bar(x - width/2, base_err, width, label='Baseline', color='#7f7f7f') # Abu-abu
bar2 = plt.bar(x + width/2, opt_err, width, label='Pasca-Optimasi', color='#2ca02c') # Hijau

plt.ylabel('Error Rate (%)')
plt.title('Perbandingan Error Rate (Semakin Rendah = Baik)', fontweight='bold')
plt.xticks(x, users)
plt.xlabel('Jumlah Users (Virtual)')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)

for rect in bar1 + bar2:
    height = rect.get_height()
    label = f'{height:.2f}%' if height > 0 else '0%'
    plt.annotate(label, xy=(rect.get_x() + rect.get_width() / 2, height),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()