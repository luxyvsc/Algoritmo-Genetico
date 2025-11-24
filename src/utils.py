from pathlib import Path
import pandas as pd
import numpy as np


def load_data(path: str = 'data/farm_data_seed42.csv'):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Data file not found: {p.resolve()}")
    df = pd.read_csv(p)
    # Espera colunas: area_id, prod, cost, water, fert, price, risk, soil_type, crop_type, seed
    prod = df['prod'].to_numpy()
    cost = df['cost'].to_numpy()
    water = df['water'].to_numpy()
    fert = df['fert'].to_numpy()
    price = df['price'].to_numpy()
    risk = df['risk'].to_numpy()
    seed = int(df['seed'].iloc[0]) if 'seed' in df.columns else None
    # soil_type e crop_type podem ser usados para análises, mas não no fitness direto
    soil_type = df['soil_type'].to_numpy()
    crop_type = df['crop_type'].to_numpy()
    return prod, cost, water, fert, price, risk, soil_type, crop_type, seed
