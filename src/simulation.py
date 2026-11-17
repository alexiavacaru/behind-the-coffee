"""Behind the Coffee — Simulation helpers.

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



def baseline_numbers(monthly):
    revenue = monthly['revenue'].sum()
    variable_cost = monthly['variable_cost'].sum()
    fixed_cost = monthly[['rent', 'salaries', 'utilities', 'other_costs']].sum().sum()
    fees = monthly['royalty'].sum() + monthly['marketing_fee'].sum()
    return {'revenue': revenue, 'variable_cost': variable_cost,
            'fixed_cost': fixed_cost, 'fee_rate': fees/revenue,
            'profit': monthly['operating_profit'].sum()}

def simulate(base, label, price=0, demand=0, variable_unit_cost=0, fixed_delta=0):
    if min(1+price, 1+demand, 1+variable_unit_cost) < 0:
        raise ValueError('Negative price, demand or unit cost is not supported')
    new_revenue = base['revenue'] * (1+price) * (1+demand)
    new_variable = base['variable_cost'] * (1+demand) * (1+variable_unit_cost)
    profit = new_revenue * (1-base['fee_rate']) - new_variable - base['fixed_cost'] - fixed_delta
    return {'scenario': label, 'revenue_ron': new_revenue,
            'operating_profit_ron': profit, 'profit_change_ron': profit-base['profit'],
            'margin_pct': profit/new_revenue*100 if new_revenue else np.nan}

def waste_summary(inventory, reduction=.20):
    df = inventory.groupby(['item','unit'],as_index=False).agg(
        consumed=('consumed','sum'), waste=('waste','sum'), purchased=('purchased','sum'))
    df['waste_rate_pct'] = 100*df['waste']/(df['consumed']+df['waste']).replace(0,np.nan)
    df['waste_after_reduction'] = df['waste']*(1-reduction)
    df['units_saved'] = df['waste']*reduction
    return df

def staff_needed(hourly, minutes_per_item=2.5, productive_fraction=.80):
    if not 0 < productive_fraction <= 1:
        raise ValueError('Productive fraction must be between 0 and 1')
    df = hourly.copy()
    df['staff_needed'] = np.ceil(df['quantity']*minutes_per_item/(60*productive_fraction)).astype(int)
    return df

def max_demand_loss(base, price_increase):
    per_unit_demand_contribution = (base['revenue'] * (1+price_increase) *
                                    (1-base['fee_rate']) - base['variable_cost'])
    if per_unit_demand_contribution <= 0:
        return np.nan
    required_multiplier = (base['profit']+base['fixed_cost']) / per_unit_demand_contribution
    return max(0, (1-required_multiplier)*100)


def compare_scenarios(base):
    """A few what-if questions I want to test against the baseline."""
    options = [
        simulate(base, 'Base'),
        simulate(base, 'Ingredients +10%', variable_unit_cost=.10),
        simulate(base, 'Prices +5%, same demand', price=.05),
        simulate(base, 'Prices +5%, demand -5%', price=.05, demand=-.05),
        simulate(base, 'Demand +10%', demand=.10),
        simulate(base, 'Fixed costs +1,500 RON', fixed_delta=1500),
    ]
    return pd.DataFrame(options)
