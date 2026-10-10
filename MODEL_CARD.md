# AgriShield AI/ML model card

## What the application does

AgriShield uses a trained Random Forest regression pipeline to estimate total
crop production from farm size, recorded rainfall, temperature, soil moisture,
and a crop-health proxy. Farmers and bankers can compare that estimate with a
user-entered climate scenario. The application can also estimate crop-funded
repayment coverage when the user supplies a same-period crop price, production
cost, and scheduled installment.

This is an AI/ML-assisted agricultural decision-support demo, not an automated
credit-underwriting system. The app does not produce a repayment/default
probability. Its separately displayed financial-history indicator is a simple,
unvalidated rule—not an ML prediction.

## Trained model: crop production

- **Target:** `Yield_tons`, generated total production in tons.
- **Features:** `Rainfall_mm`, `Temperature_C`, `Soil_Moisture`,
  `Farm_Size_acres`, and `Crop_Health_Index`.
- **Estimator:** median imputation followed by a 300-tree
  `RandomForestRegressor`, with `min_samples_leaf=2` and `random_state=42`.
- **Training/evaluation:** reproducible shuffled 80/20 train/test split with
  `random_state=42`. Imputation is fit on the training partition only. The
  trainer reports MAE, RMSE, and R-squared on the held-out partition and saves
  the fitted pipeline and metadata to `artifacts/yield_model.joblib`.
- **Current sample holdout result:** MAE 0.5598 tons, RMSE 0.7504 tons,
  R-squared 0.8449 on 100 held-out rows from the bundled synthetic dataset.
  These are synthetic-data results, not field or credit-risk validation.
- **Total vs per-acre yield:** the model predicts total tons. The application
  calculates tons per acre by dividing by selected farm size and rejects
  invalid/non-positive area.
- **Scenario method:** compare the model output for the selected CSV row with
  the output for user-entered rainfall, temperature, soil moisture, and
  crop-health values while holding farm size fixed. The reported input drivers
  are one-input-at-a-time model sensitivities, not causal effects or SHAP
  attributions.

The checked-in `crop_data.csv` has 500 generated sample records. Its weather,
crop-health proxy, farmer and loan profiles, repayment-history categories, and
yield target are simulated. The yield target is formula-generated from farm
size, rainfall, temperature, soil moisture, and crop-health proxy with added
noise. Holdout metrics therefore show recovery of patterns in synthetic data;
they do not validate field performance. The current source has no verified
satellite observations, location, season/date, weather forecast, weather
provider timestamp, measured production labels, or crop-specific weather
calibration. Crop type, irrigation, soil type, and historical yield are shown
in the farmer profile but are not model inputs: the generated `Yield_tons`
target formula does not use them, so training on those independent synthetic
fields would make the model appear domain-aware without evidence that they
improve prediction. A real field dataset should contain enough crop/location
and seasonal outcomes to evaluate them properly.

## Repayment assessment and important limit

There are no genuine, time-aligned successful-repayment or default labels.
Training a credit-risk classifier on the bundled repayment-history categories
would be misleading: they are generated labels, not verified future outcomes.
The application therefore does not report a model-derived repayment probability
or convert synthetic outputs into one.

The available 0-100 financial indicator is separate from the yield ML model.
It averages an ordinal mapping of the generated repayment-history category and
the outstanding/original-loan balance share, then assigns Low, Medium, or High
using unvalidated thresholds. It is neither a probability nor a lending
recommendation.

The optional crop-funded repayment coverage calculation uses:

```text
estimated gross crop revenue = scenario-predicted total tons × user-entered price per ton
estimated crop funds         = gross crop revenue - user-entered production costs
coverage ratio               = estimated crop funds / user-entered scheduled repayment
```

The user must supply all financial inputs for the same crop and repayment
period. The dataset contains no verified market price, production cost,
scheduled payment, or household income. This arithmetic estimate is not a
default probability and does not measure other income or household expenses.

## Explainability and appropriate interpretation

- The feature importance display is **global** and describes the yield model,
  not credit risk.
- Per-scenario driver rows show the yield model's isolated change when one
  entered feature is changed and others are held at the selected-record values.
- These effects are model sensitivities, not causal claims, validated
  credit-risk explanations, or a substitute for field verification.
- Farmer and banker pages label the bundled records as generated sample data
  and climate inputs as scenarios rather than forecasts.

## Data required for a validated climate-adjusted credit model

Obtain consented and legally usable repayment outcomes aligned to the decision
date, scheduled and actual installments, documented loan and repayment-capacity
fields, farm location and crop season, timestamped local weather forecasts and
observations, verified satellite/crop-health readings, measured yields, market
prices, and production costs. Prevent post-decision leakage; split evaluation
by time and preferably by farmer/geography; compare to simple baselines; report
precision, recall, F1, ROC-AUC, PR-AUC, calibration, subgroup performance, and
data limitations. Validate thresholds and governance before operational use.

## Windows commands

From the project directory:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe train_yield_model.py
.\venv\Scripts\python.exe -m streamlit run app.py
```

Run the tests:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

The artifact is loaded with joblib. Only load files produced by this project's
trusted training command; joblib artifacts from untrusted sources can execute
code when loaded.
