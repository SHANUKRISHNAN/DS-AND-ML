from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sklearn.ensemble import GradientBoostingRegressor
from model_common import evaluate
from config import MODELS, REPORTS
import joblib

model=GradientBoostingRegressor(n_estimators=200,learning_rate=0.05,max_depth=3,random_state=42)
df,pipe,pred,yte,m=evaluate('Gradient Boosting',model)
joblib.dump(pipe,MODELS/'gradient_boosting.joblib')
REPORTS.joinpath('day09_metrics.txt').write_text(str(m),encoding='utf-8')
print(m)
