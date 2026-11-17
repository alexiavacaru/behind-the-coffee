"""Behind the Coffee — Analysis helpers.

Small, reusable functions for my simulated coffee-shop case study.
Works with CSV files uploaded directly to Google Colab (/content).
No GitHub connection or src folder is needed.
"""

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



def break_even(monthly, total_items, n_days):
    revenue = monthly['revenue'].sum()
    variable = monthly['variable_cost'].sum()
    fees = monthly['royalty'].sum() + monthly['marketing_fee'].sum()
    fixed = monthly[['rent','salaries','utilities','other_costs']].sum().sum()
    net_ratio = (revenue - variable - fees) / revenue
    if net_ratio <= 0:
        raise ValueError('Non-positive net contribution ratio')
    required_revenue = fixed / net_ratio
    avg_revenue_per_item = revenue / total_items
    return {
        'net_contribution_ratio': net_ratio,
        'fixed_costs': fixed,
        'break_even_revenue_period': required_revenue,
        'break_even_revenue_month': required_revenue / len(monthly),
        'margin_of_safety_pct': (revenue - required_revenue) / revenue * 100,
        'break_even_items_per_day': required_revenue / avg_revenue_per_item / n_days,
        'actual_items_per_day': total_items / n_days,
    }


def sales_summary(sales):
    """A quick overview of the sales figures in RON."""
    return {'revenue_ron': float(sales['revenue'].sum()),
            'items_sold': float(sales['quantity'].sum()),
            'variable_cost_ron': float(sales['variable_cost'].sum()),
            'contribution_ron': float(sales['contribution_margin'].sum())}


def product_summary(sales, products):
    """Compare how much each product sells and contributes."""
    result = sales.groupby('product_id', as_index=False).agg(
        items=('quantity', 'sum'), revenue=('revenue', 'sum'),
        contribution=('contribution_margin', 'sum'))
    return result.merge(products[['product_id', 'product_name']], on='product_id')
