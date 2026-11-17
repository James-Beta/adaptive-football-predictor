# Football Predictor

Predicts the outcome of upcoming matches in the top five European leagues
(England, Spain, Germany, Italy, France) and shows the results in a Streamlit
app.

The model is simple and deliberately transparent: three independent
`RandomForestClassifier`s (home win / draw / away win) plus two goal
regressors, trained on rolling team-form features and pre-match betting odds.
There is no incremental/continuous learning — the model is retrained from
scratch whenever new results arrive.

---

## End-to-end flow

```
football-data.co.uk ─┐
OpenFootball ────────┼─► fixtures ─┐
The Odds API ────────┘             │
                                   ├─► clean + merge ─► model ─► app
football-data.co.uk ───► history ─► features ─┘
```

1. **History** — football-data.co.uk season CSVs (`data/raw/season_XXXX.parquet`),
   cleaned and combined. Finished seasons are downloaded once and reused
   forever; the in-progress season is refreshed.
2. **Fixtures** — three sources merged:
   - football-data.co.uk `fixtures.csv`: short horizon (about a week), but
     already carries odds.
   - OpenFootball: keyless full-season schedules, so fixtures are visible even
     during international breaks. No odds.
   - The Odds API: real market odds for the top five leagues. Optional; needs
     `ODDS_API_KEY`.
3. **Features** — rolling 5-match attacking/defensive form per team, plus odds
   converted to implied probabilities (`1 / decimal_odds`). Live fixtures use a
   separate snapshot (`latest_form.parquet`) that *includes* each team's most
   recent completed match; training rows deliberately exclude their own match
   to avoid leakage.
4. **Model** — `SimpleMatchPredictor` (`models/predictor.py`). Validation
   metrics are logged to `logs/performance_log.csv`; the checkpoint is
   `checkpoints/model_latest.pkl`.
5. **Predictions** — only fixtures with a complete odds set are predicted.
   Fixtures without odds stay visible in the app under “Odds pending” instead
   of being fed zero-filled odds.
6. **App** — `app/streamlit_app.py`: raw fixtures, team form, live predictions,
   classifier performance.

---

## Setup

Use the `football_predictor` conda environment — the base interpreter does not
have `scikit-learn`/`joblib`.

```bat
call C:\Users\HP\anaconda3\Scripts\activate.bat football_predictor
pip install -r requirements.txt
```

Optional but recommended — real odds from The Odds API
(https://the-odds-api.com, free tier = 500 credits/month):

```bat
set ODDS_API_KEY=your_key_here
```

PowerShell:

```powershell
$env:ODDS_API_KEY = "your_key_here"
```

Without a key the pipeline still runs; OpenFootball supplies the schedule and
those fixtures appear as “Odds pending”.

---

## Commands

| Command | What it does |
| --- | --- |
| `python run_pipeline.py` | Normal run: cached fixtures (6h) and history (24h), refresh only what is stale. |
| `python run_pipeline.py --refresh-current` | Refresh fixtures and the in-progress season, reuse cached finished seasons. **This is what the daily run uses.** |
| `python run_pipeline.py --force-refresh` | Re-download everything, including finished seasons. Manual full rebuild only. |
| `python train_model.py` | Retrain from scratch, save the checkpoint, append validation metrics to `logs/performance_log.csv`. |
| `python run_live_predictions.py` | Predict fixtures with complete odds; writes `data/predictions/upcoming_predictions.csv` and appends to `logs/prediction_log.csv`. |
| `python simulate_backtest.py` | Walk-forward backtest (train on the past, predict each future matchday). |
| `streamlit run app/streamlit_app.py` | Start the app. |
| `daily_run.bat` | Full daily cycle: pipeline → train → predict → git push. |

### Backtest options

```bat
python simulate_backtest.py                       :: default: from 2025-08-01, refit every 5 matchdays
python simulate_backtest.py --refit-every 1       :: strict walk-forward (slow)
python simulate_backtest.py --mask-odds           :: form-only model, no betting odds
python simulate_backtest.py --max-matchdays 5     :: quick smoke test
```

Per-matchday results are appended to `logs/backtest_log.csv`.

---

## Data files

| Path | Contents |
| --- | --- |
| `data/raw/season_XXXX.parquet` | Per-season football-data history. |
| `data/raw/odds/<DIV>.parquet` | Cached The Odds API responses (kept while fresh). |
| `data/processed/train_data.parquet` | Every historical match with engineered features. |
| `data/processed/team_metrics.parquet` | Rolling form rows (one per team per match). |
| `data/processed/latest_form.parquet` | Current form snapshot, including each team's latest match. |
| `data/processed/fixtures.parquet` | Upcoming merged fixtures + `Has_Odds`. |
| `data/processed/fixtures_meta.json` | When the last successful fixture fetch ran, row/source/odds counts. |
| `data/predictions/upcoming_predictions.csv` | What the app displays. |
| `data/reference/team_aliases.csv` | OpenFootball → football-data team-name mappings. |
| `logs/performance_log.csv` | Validation metrics per training run. |
| `logs/prediction_log.csv` | Historical predictions. |
| `logs/backtest_log.csv` | Walk-forward backtest results. |
| `logs/odds_api_usage.csv` | Odds API credits remaining per request. |

---

## Notes and caveats

- **No imputation for missing odds.** The model was trained with odds features,
  so a fixture missing any of them is skipped rather than guessed at.
- **Empty fixture fetches never overwrite good data.** If every source returns
  nothing (international break, feed outage), the last good
  `fixtures.parquet` is kept.
- **Team names are normalised, never guessed.** Unknown names are dropped with a
  warning listing exactly what needs adding to
  `data/reference/team_aliases.csv`.
- **Odds features are implied probabilities**, not decimal odds, in both
  training and live fixtures. `logs/prediction_log.csv` still contains older
  rows with decimal odds under `AvgH/AvgD/AvgA`; new rows log implied
  probabilities as `Implied_Home/Draw/Away`.
- The 90/10 validation split is chronological, and after scoring the holdout
  the model is refit on the full dataset so the saved checkpoint sees the most
  recent matches.
- Only the deployable parts are tracked in git (`app/`, `data/`, `logs/`,
  `README.md`); backend code and raw caches stay local.
