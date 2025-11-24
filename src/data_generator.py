from pathlib import Path
import numpy as np
import pandas as pd

def generate_and_save(path: str = 'data/farm_data_seed42.csv', N: int = 100, seed: int = 42):
    """Gera N áreas com produtividade e custo e salva em CSV.

    Salva também o seed no arquivo como coluna 'seed' para reprodutibilidade.
    """
    rng = np.random.default_rng(seed)
    prod = rng.uniform(10, 100, size=N)  # produtividade estimada
    cost = rng.uniform(1, 50, size=N)    # custo total
    water = rng.uniform(5, 30, size=N)   # consumo de água (m3)
    fert = rng.uniform(2, 15, size=N)    # consumo de fertilizante (kg)
    price = rng.uniform(0.8, 2.0, size=N) # preço de venda por unidade
    risk = rng.uniform(0, 10, size=N)    # índice de risco (0=baixo, 10=alto)
    soil_types = rng.choice(['argiloso', 'arenoso', 'siltoso'], size=N)
    crop_types = rng.choice(['soja', 'milho', 'algodao', 'trigo'], size=N)
    df = pd.DataFrame({
        'area_id': range(N),
        'prod': prod,
        'cost': cost,
        'water': water,
        'fert': fert,
        'price': price,
        'risk': risk,
        'soil_type': soil_types,
        'crop_type': crop_types,
        'seed': seed
    })
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
    print(f"Saved {N} samples to {p.resolve()}")

if __name__ == '__main__':
    # default run when executed as script
    generate_and_save()
