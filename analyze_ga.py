import matplotlib.pyplot as plt
import pandas as pd

from src.data_generator import generate_and_save
from src.utils import load_data
from src.ga_core import run_ga, run_ga_grid_search

# 1. Gerar dados realistas
generate_and_save(path='data/farm_data_seed42.csv', N=100, seed=42)

# 2. Carregar dados
prod, cost, water, fert, price, risk, soil_type, crop_type, seed = load_data('data/farm_data_seed42.csv')

# 3. Definir limites e parâmetros do GA
budget = 1200
water_limit = 1200
fert_limit = 600

# 4. Executar Algoritmo Genético
best, res = run_ga(
    prod, cost, water, fert, price, risk,
    budget, water_limit, fert_limit,
    pop_size=100, n_gens=100, rng=None, verbose=True
)

print(f"\nMelhor fitness: {res['best_fitness']}")
print(f"Tempo de execução: {res['time_seconds']:.3f} segundos")

# 5. Estatísticas das áreas selecionadas
selected_idx = [i for i, v in enumerate(best) if v == 1]
print(f"\nTotal de áreas selecionadas: {len(selected_idx)}")
if selected_idx:
    print(f"IDs das áreas selecionadas: {selected_idx}")
    print(f"Produtividade total: {sum(prod[selected_idx]):.2f} toneladas")
    print(f"Custo total: {sum(cost[selected_idx]):.2f}")
    print(f"Consumo total de água: {sum(water[selected_idx]):.2f} m³")
    print(f"Consumo total de fertilizante: {sum(fert[selected_idx]):.2f} kg")
    print(f"Receita total: {sum(prod[selected_idx] * price[selected_idx]):.2f}")
    print(f"Risco total: {sum(risk[selected_idx]):.2f} (índice 0-10)")
    print(f"Tipos de solo presentes: {', '.join(set(soil_type[selected_idx]))}")
    print(f"Culturas presentes: {', '.join(set(crop_type[selected_idx]))}")

# 6. Penalidades aplicadas
def calc_penalty(cost, water, fert, budget, water_limit, fert_limit):
    penalty = 0.0
    if cost > budget:
        penalty += (cost - budget) * 2.0
    if water > water_limit:
        penalty += (water - water_limit) * 1.5
    if fert > fert_limit:
        penalty += (fert - fert_limit) * 1.2
    return penalty

penalty = calc_penalty(
    sum(cost[selected_idx]),
    sum(water[selected_idx]),
    sum(fert[selected_idx]),
    budget, water_limit, fert_limit
)
print(f"Penalidade total aplicada por exceder limites: {penalty:.2f}")

# 7. Distribuição dos atributos das áreas selecionadas
df = pd.DataFrame({
    'prod': prod,
    'cost': cost,
    'water': water,
    'fert': fert,
    'price': price,
    'risk': risk,
    'soil_type': soil_type,
    'crop_type': crop_type
})
selected_df = df.iloc[selected_idx]
print("\nResumo estatístico das áreas selecionadas:")
desc = selected_df.describe().copy()
desc.loc['mean'] = desc.loc['mean'].round(2)
desc.loc['std'] = desc.loc['std'].round(2)
desc.loc['min'] = desc.loc['min'].round(2)
desc.loc['max'] = desc.loc['max'].round(2)
print(desc)

# 8. Ranking das áreas por produtividade e risco
if len(selected_idx) > 0:
    print("\nTop 5 áreas por produtividade:")
    print(selected_df.sort_values('prod', ascending=False).head(5)[['prod', 'cost', 'risk', 'soil_type', 'crop_type']].round(2))
    print("\nTop 5 áreas por menor risco:")
    print(selected_df.sort_values('risk', ascending=True).head(5)[['prod', 'cost', 'risk', 'soil_type', 'crop_type']].round(2))

# 9. Recursos totais utilizados vs limites
print(f"\nRecursos totais utilizados vs limites:")
print(f"Custo: {sum(cost[selected_idx]):.2f} / Limite: {budget}")
print(f"Água: {sum(water[selected_idx]):.2f} / Limite: {water_limit} m³")
print(f"Fertilizante: {sum(fert[selected_idx]):.2f} / Limite: {fert_limit} kg")

# 10. Análise gráfica da convergência
plt.figure(figsize=(10,5))
plt.plot(res['history']['best_fitness'], label='Best Fitness')
plt.plot(res['history']['mean_fitness'], label='Mean Fitness')
plt.xlabel('Geração')
plt.ylabel('Fitness')
plt.title('Convergência do Algoritmo Genético')
plt.legend()
plt.tight_layout()

# 11. Boxplot dos fitness por geração
plt.figure(figsize=(8,4))
plt.boxplot(res['history']['best_fitness'], vert=False)
plt.title('Boxplot do Best Fitness por geração')
plt.xlabel('Fitness')
plt.tight_layout()
plt.show()