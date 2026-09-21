"""Run the full EcoTwin pipeline in order. Execute from the project root with: python src/run_all.py"""
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scripts=['day03_cleaning.py','day04_eda_part1.py','day05_eda_part2.py','day06_feature_engineering.py','day07_linear_regression.py','day08_random_forest.py','day09_gradient_boosting.py','day10_model_selection.py','day11_rl_concepts.py','day12_create_environment.py','day13_manual_environment_test.py']
for s in scripts:
    print('\n'+'='*70+'\nRUNNING '+s+'\n'+'='*70)
    subprocess.run([sys.executable,str(ROOT/'src'/s)],cwd=ROOT,check=True)
print('\nALL STEPS COMPLETED SUCCESSFULLY.')
