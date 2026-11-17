from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path('/content') if Path('/content').is_dir() else Path.cwd()
FIGURES = PROJECT_ROOT / 'reports' / 'figures'
TABLES = PROJECT_ROOT / 'reports' / 'tables'
FIGURES.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

def read_data(folder, filename):
    path = PROJECT_ROOT / filename
    if not path.is_file():
        raise FileNotFoundError(f'Missing {filename}. Run the upload cell at the top of this notebook.')
    df = pd.read_csv(path)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

def save_plot(filename):
    plt.tight_layout()
    plt.savefig(FIGURES / filename, dpi=150, bbox_inches='tight')
    plt.close()

def save_table(df, filename):
    df.to_csv(TABLES / filename, index=False)

def check_close(actual, expected, label, tolerance=0.06):
    if not np.isclose(actual, expected, atol=tolerance):
        raise ValueError(f'{label}: {actual:.2f} != {expected:.2f}')

def quality_report(datasets):
    for name, df in datasets.items():
        print(f'{name}: {len(df)} rows; missing={df.isna().sum().sum()}; duplicates={df.duplicated().sum()}')

pd.set_option('display.float_format', '{:,.2f}'.format)

from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

FEATURES = ['hour', 'weekday', 'is_weekend', 'day_of_year', 'month_number']
TARGET = 'quantity'

def load_model_data():
    df = read_data('processed', 'model_dataset.csv')
    return df.sort_values(['date', 'hour']).reset_index(drop=True)

def add_features(df):
    df = df.copy()
    df['weekday'] = df['date'].dt.weekday
    df['is_weekend'] = (df['weekday'] >= 5).astype(int)
    df['day_of_year'] = df['date'].dt.dayofyear
    df['month_number'] = df['date'].dt.month
    return df

def split_by_date(df):
    dates = np.sort(df['date'].unique())
    first = pd.Timestamp(dates[int(len(dates) * .60)])
    second = pd.Timestamp(dates[int(len(dates) * .80)])
    return (df['date'] < first,
            (df['date'] >= first) & (df['date'] < second),
            df['date'] >= second, first, second)

def baseline_predict(train_df, predict_df):
    lookup = train_df.groupby(['weekday', 'hour'])[TARGET].mean()
    fallback = train_df[TARGET].mean()
    return np.array([lookup.get((int(w), int(h)), fallback)
                     for w, h in zip(predict_df['weekday'], predict_df['hour'])])

def scores(actual, predicted):
    a, p = np.asarray(actual), np.asarray(predicted)
    return {'MAE': mean_absolute_error(a, p),
            'RMSE': np.sqrt(mean_squared_error(a, p)),
            'WAPE_pct': 100 * np.abs(a-p).sum() / a.sum() if a.sum() else np.nan}

def get_models():
    return {'Random forest': RandomForestRegressor(n_estimators=250, min_samples_leaf=3,
                                                   random_state=42, n_jobs=-1),
            'Gradient boosting': HistGradientBoostingRegressor(max_iter=120,
                                                               max_leaf_nodes=15, random_state=42)}

def compare_models(train_df, validation_df):
    """Check if a machine-learning model beats a simple weekday/hour average."""
    rows = []
    baseline = baseline_predict(train_df, validation_df)
    rows.append({'model': 'Weekday/hour baseline',
                 **scores(validation_df[TARGET], baseline)})
    for name, estimator in get_models().items():
        estimator.fit(train_df[FEATURES], train_df[TARGET])
        prediction = np.maximum(0, estimator.predict(validation_df[FEATURES]))
        rows.append({'model': name, **scores(validation_df[TARGET], prediction)})
    return pd.DataFrame(rows).sort_values('MAE').reset_index(drop=True)
