import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from config import FEATURE_DATA, MODELS, REPORTS
from utils import TARGET

DROP=['co2_concentration_ppm','timestamp','reward_value']

def make_data():
    df=pd.read_csv(FEATURE_DATA,parse_dates=['timestamp'])
    X=df.drop(columns=DROP); y=df[TARGET]
    cats=X.select_dtypes(include=['object']).columns.tolist()
    nums=[c for c in X.columns if c not in cats]
    pre=ColumnTransformer([
        ('num',SimpleImputer(strategy='median'),nums),
        ('cat',Pipeline([('imp',SimpleImputer(strategy='most_frequent')),('oh',OneHotEncoder(handle_unknown='ignore'))]),cats)
    ])
    split=int(len(df)*0.8)
    return df,X.iloc[:split],X.iloc[split:],y.iloc[:split],y.iloc[split:],pre

def evaluate(name, model):
    df,Xtr,Xte,ytr,yte,pre=make_data()
    pipe=Pipeline([('preprocessor',pre),('model',model)])
    pipe.fit(Xtr,ytr); pred=pipe.predict(Xte)
    metrics={'model':name,'MAE':mean_absolute_error(yte,pred),'RMSE':mean_squared_error(yte,pred)**0.5,'R2':r2_score(yte,pred)}
    return df,pipe,pred,yte,metrics
