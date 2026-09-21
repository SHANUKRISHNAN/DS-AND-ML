import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pandas as pd
from config import FEATURE_DATA, REPORTS
from rl_environment import EcoTwinEnv

df=pd.read_csv(FEATURE_DATA,parse_dates=['timestamp'])
env=EcoTwinEnv(df)
rows=[]
for action in range(5):
    env.reset(0)
    _,reward,done,info=env.step(action)
    rows.append({'action':action,'action_name':info['action_name'],'co2_before_ppm':info['co2_before'],'co2_after_ppm':info['co2_after'],'reduction_ppm':reward,'done':done})
out=pd.DataFrame(rows)
out.to_csv(REPORTS/'day13_action_test.csv',index=False)
print(out.to_string(index=False))
