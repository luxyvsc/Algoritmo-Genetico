import json
from pathlib import Path
import argparse
import time
import numpy as np

# Support running as module (python -m src.experiments) or as script (python src\experiments.py)
try:
    from .data_generator import generate_and_save
    from .utils import load_data
    from .ga_core import run_ga
except Exception:
    from data_generator import generate_and_save
    from utils import load_data
    from ga_core import run_ga



def run_experiment_from_config(config_path: str, save_csv: bool = True):
    p = Path(config_path)
    cfgs = json.loads(p.read_text())
    # Permite lista de configs ou único config
    if isinstance(cfgs, dict):
        cfgs = [cfgs]
    results = []
    results_dir = Path('results')
    results_dir.mkdir(parents=True, exist_ok=True)
    for idx, cfg in enumerate(cfgs):
        print(f"\n--- Rodando experimento {idx+1}/{len(cfgs)} ---")
        data_path = cfg.get('data_path', 'data/farm_data_seed42.csv')
        if not Path(data_path).exists():
            generate_and_save(path=data_path, N=cfg.get('N', 100), seed=cfg.get('seed', 42))
        prod, cost, water, fert, price, risk, soil_type, crop_type, seed = load_data(data_path)
        budget = cfg.get('budget', 1200)
        water_limit = cfg.get('water_limit', 1200)
        fert_limit = cfg.get('fert_limit', 600)
        rng = np.random.default_rng(cfg.get('seed', None))
        best, res = run_ga(
            prod, cost, water, fert, price, risk,
            budget=budget,
            water_limit=water_limit,
            fert_limit=fert_limit,
            pop_size=cfg.get('pop_size', 100),
            n_gens=cfg.get('n_gens', 100),
            mutation_rate=cfg.get('mutation_rate', 0.01),
            selection_method=cfg.get('selection', 'tournament'),
            tournament_k=cfg.get('tournament_k', 3),
            crossover_method=cfg.get('crossover', 'two_point'),
            mutation_method=cfg.get('mutation', 'bit_flip'),
            elitism=cfg.get('elitism', 1),
            rng=rng,
            verbose=True
        )
        out = {
            'config': cfg,
            'best_fitness': float(res['best_fitness']),
            'time_seconds': float(res['time_seconds']),
            'selection_method': cfg.get('selection', 'tournament'),
            'crossover_method': cfg.get('crossover', 'two_point'),
            'mutation_method': cfg.get('mutation', 'bit_flip'),
            'best_vector': best.tolist()
        }
        results.append(out)
    timestamp = int(time.time())
    out_path = results_dir / f"result_seed{cfg.get('seed', 'na')}_exp{idx+1}_{timestamp}.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"Wrote result to {out_path}")
    # Exportar CSV
    if save_csv:
        import pandas as pd
        df = pd.DataFrame(results)
        csv_path = results_dir / "batch_results.csv"
        df.to_csv(csv_path, index=False)
        print(f"Batch results saved to {csv_path}")



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='configs/baseline.json')
    parser.add_argument('--no-csv', action='store_true', help='Não exportar CSV dos resultados')
    args = parser.parse_args()
    run_experiment_from_config(args.config, save_csv=not args.no_csv)


if __name__ == '__main__':
    main()
