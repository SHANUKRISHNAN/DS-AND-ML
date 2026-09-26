import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
from config import PROCESSED_DATA, FIGURES, REPORTS


df = __import__('pandas').read_csv(PROCESSED_DATA, parse_dates=['timestamp'])

def save(fig, name):
    fig.tight_layout(); fig.savefig(FIGURES / name, dpi=160); plt.close(fig)

fig = plt.figure(figsize=(9,5)); plt.hist(df['co2_concentration_ppm'], bins=30); plt.xlabel('CO2 concentration (ppm)'); plt.ylabel('Frequency'); plt.title('CO2 Distribution'); save(fig,'day04_co2_distribution.png')

hourly = df.groupby(df.timestamp.dt.hour)['co2_concentration_ppm'].mean()
fig = plt.figure(figsize=(9,5)); plt.plot(hourly.index, hourly.values, marker='o'); plt.xlabel('Hour'); plt.ylabel('Mean CO2 (ppm)'); plt.title('Mean CO2 by Hour'); plt.grid(alpha=.25); save(fig,'day04_co2_over_time.png')

fig = plt.figure(figsize=(8,5)); plt.scatter(df['traffic_emission_rate_kg_h'], df['co2_concentration_ppm'], alpha=.55); plt.xlabel('Traffic emission rate (kg/h)'); plt.ylabel('CO2 (ppm)'); plt.title('Traffic Emission vs CO2'); save(fig,'day04_traffic_vs_co2.png')

fig = plt.figure(figsize=(8,5)); plt.scatter(df['wind_speed_ms'], df['co2_concentration_ppm'], alpha=.55); plt.xlabel('Wind speed (m/s)'); plt.ylabel('CO2 (ppm)'); plt.title('Wind Speed vs CO2'); save(fig,'day04_wind_vs_co2.png')

corr1 = df['traffic_emission_rate_kg_h'].corr(df['co2_concentration_ppm'])
corr2 = df['wind_speed_ms'].corr(df['co2_concentration_ppm'])
text=f"Day 4 EDA Part 1\nTraffic vs CO2 Pearson correlation: {corr1:.4f}\nWind speed vs CO2 Pearson correlation: {corr2:.4f}\nFigures saved in outputs/figures.\n"
(REPORTS/'day04_eda_summary.txt').write_text(text,encoding='utf-8'); print(text)
