import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor,GradientBoostingRegressor
from model_common import evaluate
from config import REPORTS,FIGURES,MODELS

models=[('Linear Regression',LinearRegression()),('Random Forest',RandomForestRegressor(n_estimators=250,random_state=42,n_jobs=-1)),('Gradient Boosting',GradientBoostingRegressor(n_estimators=200,learning_rate=.05,max_depth=3,random_state=42))]
rows=[]
for name,model in models:
    df,pipe,pred,yte,m=evaluate(name,model); rows.append(m)
    # save predictions for every model
    pd.DataFrame({'actual_co2_ppm':yte.values,'predicted_co2_ppm':pred}).to_csv(REPORTS/(name.lower().replace(' ','_')+'_predictions.csv'),index=False)
res=pd.DataFrame(rows).sort_values('RMSE')
res.to_csv(REPORTS/'model_comparison.csv',index=False)

fig=plt.figure(figsize=(9,5)); plt.bar(res['model'],res['RMSE']); plt.ylabel('RMSE (ppm)'); plt.title('Model Comparison - RMSE'); plt.xticks(rotation=15); fig.tight_layout(); fig.savefig(FIGURES/'day10_model_comparison.png',dpi=160); plt.close(fig)

best_name=res.iloc[0]['model']
model_map={n:m for n,m in models}; _,best_pipe,pred,yte,_=evaluate(best_name,model_map[best_name])
# Actual vs predicted
fig=plt.figure(figsize=(7,7)); plt.scatter(yte,pred,alpha=.55); lo=min(yte.min(),pred.min()); hi=max(yte.max(),pred.max()); plt.plot([lo,hi],[lo,hi],linestyle='--'); plt.xlabel('Actual CO2 (ppm)'); plt.ylabel('Predicted CO2 (ppm)'); plt.title(f'Actual vs Predicted - {best_name}'); fig.tight_layout(); fig.savefig(FIGURES/'day10_actual_vs_predicted.png',dpi=160); plt.close(fig)

# Feature importance where supported; use transformed feature names.
try:
    prep=best_pipe.named_steps['preprocessor']; estimator=best_pipe.named_steps['model']; names=prep.get_feature_names_out(); imp=estimator.feature_importances_; fi=pd.DataFrame({'feature':names,'importance':imp}).sort_values('importance',ascending=False).head(15); fi.to_csv(REPORTS/'feature_importance_top15.csv',index=False)
    fig=plt.figure(figsize=(9,6)); plt.barh(fi['feature'][::-1],fi['importance'][::-1]); plt.xlabel('Importance'); plt.title(f'Top Feature Importance - {best_name}'); fig.tight_layout(); fig.savefig(FIGURES/'day10_feature_importance.png',dpi=160); plt.close(fig)
except Exception as e:
    (REPORTS/'feature_importance_error.txt').write_text(str(e),encoding='utf-8')

text='Model comparison:\n'+res.to_string(index=False)+f'\n\nLowest RMSE in this chronological holdout: {best_name}.\nNote: a negative R2 means the model did not outperform the mean baseline on this synthetic dataset. This is a valid result and should be documented rather than hidden.\n'
(REPORTS/'day10_model_selection_summary.txt').write_text(text,encoding='utf-8'); print(text)
