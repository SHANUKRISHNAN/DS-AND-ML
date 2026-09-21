<<<<<<< HEAD
# EcoTwin: Reinforcement Learning for Urban Carbon Dispersal

This is a **working, tested VS Code project template** for the 13-day project plan. The supplied dataset is already placed in `data/raw/EcoTwin_dataset_raw.csv`.

## 1. Project goal

Build a practical Data Science + Machine Learning + Reinforcement Learning workflow:

1. collect/inspect urban sensor-style data
2. clean it
3. perform EDA
4. engineer time/environment/control features
5. train Linear Regression, Random Forest and Gradient Boosting models
6. compare MAE, RMSE and R²
7. design a small RL environment with states, actions and rewards
8. manually test five control actions

**Important:** the provided dataset is synthetic/project-style data. The RL environment in this repository is a transparent educational simulator, not a validated atmospheric dispersion model.

## 2. Exact VS Code setup (Windows PowerShell)

Open the folder in VS Code. Then Terminal → New Terminal.

```powershell
python --version
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Then select the interpreter in VS Code: `Ctrl+Shift+P` → **Python: Select Interpreter** → choose `.venv`.

## 3. Run everything at once

From the project root:

```powershell
python src/run_all.py
```

Expected final line:

```text
ALL STEPS COMPLETED SUCCESSFULLY.
```

## 4. Run each day separately

```powershell
python src/day03_cleaning.py
python src/day04_eda_part1.py
python src/day05_eda_part2.py
python src/day06_feature_engineering.py
python src/day07_linear_regression.py
python src/day08_random_forest.py
python src/day09_gradient_boosting.py
python src/day10_model_selection.py
python src/day11_rl_concepts.py
python src/day12_create_environment.py
python src/day13_manual_environment_test.py
```

Day 1 and Day 2 are setup/data inspection tasks. The raw dataset is already supplied, so the runnable pipeline begins with Day 3.

## 5. Notebook workflow

The `notebooks/` folder contains a notebook for each day. If you prefer notebooks, install the requirements and open the `.ipynb` files in VS Code. Select the `.venv` kernel.

## 6. Where the outputs go

- Clean data: `data/processed/EcoTwin_clean.csv`
- Feature data: `data/processed/EcoTwin_features.csv`
- Charts: `outputs/figures/`
- Text/CSV reports: `outputs/reports/`
- Trained models: `models/*.joblib`

## 7. Dataset columns

The supplied CSV has 1,500 rows and 16 columns:

`timestamp, zone_id, latitude, longitude, wind_speed_ms, wind_direction_deg, temperature_c, humidity_pct, traffic_emission_rate_kg_h, industrial_emission_rate_kg_h, rl_traffic_signal_offset_s, rl_green_corridor_active, rl_ventilation_control_mw, co2_concentration_ppm, pm25_ug_m3, reward_value`

Target for supervised ML: `co2_concentration_ppm`.

## 8. How to explain the ML result

Use MAE, RMSE and R². The code uses a **chronological 80/20 holdout**: first 80% for training, last 20% for testing. This avoids randomly mixing future observations into training.

Do not force a positive R². If R² is negative, report it honestly: on this supplied synthetic dataset, the model did not beat the mean baseline on the test period. This is itself an EDA/modeling finding and suggests that a stronger real-world dataset or additional predictive features are needed.

## 9. GitHub

After verifying the project works:

```powershell
git init
git add .
git commit -m "Add EcoTwin data science and RL project"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

If `origin` already exists, do not run `git remote add origin` again. Use `git remote -v` to inspect it.
=======
# DS-AND-ML
>>>>>>> 13da94ff2f4f3b2dcedbe8cf8415fadd5dd36849
