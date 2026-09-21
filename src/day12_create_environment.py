import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pandas as pd
from config import FEATURE_DATA, REPORTS
from rl_environment import EcoTwinEnv

df=pd.read_csv(FEATURE_DATA,parse_dates=['timestamp'])
env=EcoTwinEnv(df)
obs=env.reset(0)
text=f'Observation length: {len(obs)}\nInitial observation: {obs}\nAction space size: {env.action_space_n}\nObservation columns: {env.observation_columns}\n'
(REPORTS/'day12_environment_summary.txt').write_text(text,encoding='utf-8'); print(text)
