import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd
import matplotlib.pyplot as plt
from config import PROCESSED_DATA, FIGURES, REPORTS


df=pd.read_csv(PROCESSED_DATA,parse_dates=['timestamp'])
num=df.select_dtypes(include='number')
cor=num.corr()
fig=plt.figure(figsize=(12,9)); plt.imshow(cor,cmap='coolwarm',vmin=-1,vmax=1,aspect='auto'); plt.colorbar(label='Pearson correlation'); plt.xticks(range(len(cor.columns)),cor.columns,rotation=90,fontsize=7); plt.yticks(range(len(cor.columns)),cor.columns,fontsize=7); plt.title('Correlation Heatmap'); fig.tight_layout(); fig.savefig(FIGURES/'day05_correlation_heatmap.png',dpi=160); plt.close(fig)

zone=df.groupby('zone_id')['co2_concentration_ppm'].agg(['mean','max','count']).sort_values('mean',ascending=False)
zone.to_csv(REPORTS/'co2_by_zone.csv')

df['hour']=df.timestamp.dt.hour
hour=df.groupby('hour')['co2_concentration_ppm'].mean().sort_values(ascending=False)
hour.to_csv(REPORTS/'co2_by_hour.csv',header=['mean_co2_ppm'])

high=df.nlargest(10,'co2_concentration_ppm')[['timestamp','zone_id','co2_concentration_ppm','traffic_emission_rate_kg_h','wind_speed_ms']]
high.to_csv(REPORTS/'top10_high_carbon_periods.csv',index=False)

text=f"Day 5 EDA Part 2\nHighest mean-CO2 zone: {zone.index[0]} ({zone.iloc[0]['mean']:.2f} ppm)\nHighest mean-CO2 hour: {int(hour.index[0]):02d}:00 ({hour.iloc[0]:.2f} ppm)\nHighest observed CO2: {df.co2_concentration_ppm.max():.2f} ppm\nSee reports/co2_by_zone.csv, co2_by_hour.csv, top10_high_carbon_periods.csv.\n"
(REPORTS/'day05_eda_summary.txt').write_text(text,encoding='utf-8'); print(text)
