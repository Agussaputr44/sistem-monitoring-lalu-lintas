import matplotlib.pyplot as plt
import numpy as np

users = ['50', '100', '150', '200', '250']
base_tp = [0.63, 1.11, 1.18, 1.15, 1.07]
opt_tp = [4.04, 7.95, 11.89, 11.15, 9.75]

x = np.arange(len(users))
width = 0.35

plt.figure(figsize=(10, 6))
bar1 = plt.bar(x - width/2, base_tp, width, label='Baseline', color='#d62728')
bar2 = plt.bar(x + width/2, opt_tp, width, label='Pasca-Optimasi', color='#1f77b4')

plt.ylabel('Throughput (req/sec)')
plt.title('Perbandingan Throughput (Semakin Tinggi = Baik)', fontweight='bold')
plt.xticks(x, users)
plt.xlabel('Jumlah Users (Virtual)')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)

for rect in bar1 + bar2:
    height = rect.get_height()
    plt.annotate(f'{height:.2f}', xy=(rect.get_x() + rect.get_width() / 2, height),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()