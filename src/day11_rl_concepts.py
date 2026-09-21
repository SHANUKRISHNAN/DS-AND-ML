from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pandas as pd
from config import FEATURE_DATA, REPORTS

text='''EcoTwin RL design\n\nState: CO2, traffic emissions, wind, temperature, humidity, signal offset, green corridor flag, ventilation control.\nActions: 0 no control; 1 increase signal offset; 2 decrease signal offset; 3 activate green corridor; 4 increase ventilation.\nReward: positive when simulated CO2 decreases.\nEnvironment: one urban-zone observation plus a transparent control-response equation.\nThis is a learning/demo simulator; it is not a calibrated atmospheric dispersion solver.\n'''
(REPORTS/'day11_rl_design.txt').write_text(text,encoding='utf-8'); print(text)
