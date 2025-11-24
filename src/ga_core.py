from typing import Tuple, Dict, Any, Optional
import numpy as np
import time


def init_population(pop_size: int, chromosome_length: int, rng: np.random.Generator):
    return rng.integers(0, 2, size=(pop_size, chromosome_length), dtype=np.int8)



def fitness(
    chromosome: np.ndarray,
    prod: np.ndarray,
    cost: np.ndarray,
    water: np.ndarray,
    fert: np.ndarray,
    price: np.ndarray,
    risk: np.ndarray,
    budget: float,
    water_limit: float,
    fert_limit: float
) -> float:
    # Receita total
    total_revenue = float(np.sum(chromosome * prod * price))
    total_cost = float(np.sum(chromosome * cost))
    total_water = float(np.sum(chromosome * water))
    total_fert = float(np.sum(chromosome * fert))
    total_risk = float(np.sum(chromosome * risk))
    # Penalização por violar restrições
    penalty = 0.0
    if total_cost > budget:
        penalty += (total_cost - budget) * 2.0
    if total_water > water_limit:
        penalty += (total_water - water_limit) * 1.5
    if total_fert > fert_limit:
        penalty += (total_fert - fert_limit) * 1.2
    # Fitness: receita líquida menos risco e penalidades
    return total_revenue - total_cost - total_risk - penalty


def tournament_selection(pop: np.ndarray, fitnesses: np.ndarray, rng: np.random.Generator, k: int = 3):
    pop_size = len(pop)
    idx = rng.integers(0, pop_size, size=k)
    winner = idx[np.argmax(fitnesses[idx])]
    return pop[winner].copy()


def roulette_selection(pop: np.ndarray, fitnesses: np.ndarray, rng: np.random.Generator):
    # ensure non-negative
    minf = fitnesses.min()
    if minf < 0:
        fitnesses = fitnesses - minf
    s = fitnesses.sum()
    if s == 0:
        # fallback to random
        return pop[rng.integers(0, len(pop))].copy()
    probs = fitnesses / s
    idx = rng.choice(len(pop), p=probs)
    return pop[idx].copy()


def rank_selection(pop: np.ndarray, fitnesses: np.ndarray, rng: np.random.Generator):
    ranks = np.argsort(np.argsort(-fitnesses))  # higher fitness -> lower rank index
    probs = (len(fitnesses) - ranks) / np.sum(len(fitnesses) - ranks)
    idx = rng.choice(len(pop), p=probs)
    return pop[idx].copy()


def one_point_crossover(a: np.ndarray, b: np.ndarray, rng: np.random.Generator):
    L = len(a)
    if L < 2:
        return a.copy(), b.copy()
    p = rng.integers(1, L)
    c1 = np.concatenate([a[:p], b[p:]])
    c2 = np.concatenate([b[:p], a[p:]])
    return c1, c2


def two_point_crossover(a: np.ndarray, b: np.ndarray, rng: np.random.Generator):
    L = len(a)
    if L < 3:
        return one_point_crossover(a, b, rng)
    p1 = rng.integers(1, L - 1)
    p2 = rng.integers(p1 + 1, L)
    c1 = a.copy()
    c2 = b.copy()
    c1[p1:p2], c2[p1:p2] = b[p1:p2], a[p1:p2]
    return c1, c2


def uniform_crossover(a: np.ndarray, b: np.ndarray, rng: np.random.Generator):
    mask = rng.integers(0, 2, size=a.shape, dtype=bool)
    c1 = a.copy()
    c2 = b.copy()
    c1[mask] = b[mask]
    c2[mask] = a[mask]
    return c1, c2


def bit_flip_mutation(chromosome: np.ndarray, rate: float, rng: np.random.Generator):
    mask = rng.random(size=chromosome.shape) < rate
    chromosome[mask] = 1 - chromosome[mask]


def swap_mutation(chromosome: np.ndarray, rng: np.random.Generator):
    L = len(chromosome)
    if L < 2:
        return
    i, j = rng.choice(L, size=2, replace=False)
    chromosome[i], chromosome[j] = chromosome[j], chromosome[i]


def repair(chromosome: np.ndarray, weights: np.ndarray, budget: float, rng: np.random.Generator):
    # Remove items until weight <= budget: remove items with lowest value/weight first
    while np.sum(chromosome * weights) > budget:
        selected_idx = np.where(chromosome == 1)[0]
        if len(selected_idx) == 0:
            break
        ratios = (weights[selected_idx]) / (1.0 + 0)  # weight only
        # remove random among selected with probability proportional to ratio
        i = rng.choice(selected_idx)
        chromosome[i] = 0



def run_ga(
    prod: np.ndarray,
    cost: np.ndarray,
    water: np.ndarray,
    fert: np.ndarray,
    price: np.ndarray,
    risk: np.ndarray,
    budget: float,
    water_limit: float,
    fert_limit: float,
    pop_size: int = 100,
    n_gens: int = 200,
    mutation_rate: float = 0.01,
    selection_method: str = 'tournament',
    tournament_k: int = 3,
    crossover_method: str = 'one_point',
    mutation_method: str = 'bit_flip',
    elitism: int = 0,
    rng: Optional[np.random.Generator] = None,
    repair_violations: bool = False,
    stagnation_patience: int = 30,
    verbose: bool = False,
    early_stop: bool = True,
    early_stop_delta: float = 1e-3,
    early_stop_patience: int = 20
) -> Tuple[np.ndarray, Dict[str, Any]]:
    if rng is None:
        rng = np.random.default_rng()
    n_items = len(prod)
    pop = init_population(pop_size, n_items, rng)
    fitnesses = np.array([
        fitness(ind, prod, cost, water, fert, price, risk, budget, water_limit, fert_limit)
        for ind in pop
    ])
    best_idx = int(np.argmax(fitnesses))
    best = pop[best_idx].copy()
    best_fit = fitnesses[best_idx]
    history = {'best_fitness': [], 'mean_fitness': []}
    no_improve = 0
    start_time = time.perf_counter()

    stop_counter = 0
    last_best_fit = best_fit
    for gen in range(n_gens):
        new_pop = []
        # elitism: preserve top individuals
        if elitism > 0:
            elite_idx = np.argsort(-fitnesses)[:elitism]
            for ei in elite_idx:
                new_pop.append(pop[ei].copy())

        while len(new_pop) < pop_size:
            # selection
            if selection_method == 'roulette':
                p1 = roulette_selection(pop, fitnesses, rng)
                p2 = roulette_selection(pop, fitnesses, rng)
            elif selection_method == 'rank':
                p1 = rank_selection(pop, fitnesses, rng)
                p2 = rank_selection(pop, fitnesses, rng)
            else:
                p1 = tournament_selection(pop, fitnesses, rng, k=tournament_k)
                p2 = tournament_selection(pop, fitnesses, rng, k=tournament_k)

            # crossover
            if crossover_method == 'two_point':
                c1, c2 = two_point_crossover(p1, p2, rng)
            elif crossover_method == 'uniform':
                c1, c2 = uniform_crossover(p1, p2, rng)
            else:
                c1, c2 = one_point_crossover(p1, p2, rng)

            # mutation
            if mutation_method == 'swap':
                if rng.random() < mutation_rate:
                    swap_mutation(c1, rng)
                if rng.random() < mutation_rate:
                    swap_mutation(c2, rng)
            else:
                bit_flip_mutation(c1, mutation_rate, rng)
                bit_flip_mutation(c2, mutation_rate, rng)

            # O repair pode ser adaptado para múltiplos constraints se necessário
            new_pop.append(c1)
            if len(new_pop) < pop_size:
                new_pop.append(c2)

        pop = np.array(new_pop)
        fitnesses = np.array([
            fitness(ind, prod, cost, water, fert, price, risk, budget, water_limit, fert_limit)
            for ind in pop
        ])
        gen_best_idx = int(np.argmax(fitnesses))
        gen_best_fit = float(fitnesses[gen_best_idx])
        history['best_fitness'].append(gen_best_fit)
        history['mean_fitness'].append(float(np.mean(fitnesses)))

        if gen_best_fit > best_fit:
            best_fit = gen_best_fit
            best = pop[gen_best_idx].copy()
            no_improve = 0
            # Early stopping: reset counter if improved
            stop_counter = 0
        else:
            no_improve += 1
            # Early stopping: count stagnation
            if early_stop and abs(gen_best_fit - last_best_fit) < early_stop_delta:
                stop_counter += 1
            else:
                stop_counter = 0
        last_best_fit = gen_best_fit

        # adaptive mutation: if stagnated, increase mutation rate slightly
        if no_improve > 0 and (no_improve % (stagnation_patience // 3 + 1) == 0):
            mutation_rate = min(0.5, mutation_rate * 1.5)

        if no_improve >= stagnation_patience:
            # partial restart: replace half population randomly
            num_replace = pop_size // 2
            pop[:num_replace] = init_population(num_replace, n_items, rng)
            fitnesses[:num_replace] = np.array([
                fitness(ind, prod, cost, water, fert, price, risk, budget, water_limit, fert_limit)
                for ind in pop[:num_replace]
            ])
            no_improve = 0

        # Logging opcional
        if verbose and (gen % 10 == 0 or gen == n_gens - 1):
            print(f"Geração {gen:3d}: Best Fitness = {gen_best_fit:.2f}, Mean Fitness = {history['mean_fitness'][-1]:.2f}")

        # Early stopping: interrompe se estagnado
        if early_stop and stop_counter >= early_stop_patience:
            if verbose:
                print(f"Early stopping ativado na geração {gen}. Melhor fitness: {best_fit:.2f}")
            break

    elapsed = time.perf_counter() - start_time
    result = {'best': best, 'best_fitness': best_fit, 'time_seconds': elapsed, 'history': history}

    return best, result


# Função para testar todas as combinações de métodos e escolher o melhor
def run_ga_grid_search(
    prod: np.ndarray,
    cost: np.ndarray,
    water: np.ndarray,
    fert: np.ndarray,
    price: np.ndarray,
    risk: np.ndarray,
    budget: float,
    water_limit: float,
    fert_limit: float,
    pop_size: int = 100,
    n_gens: int = 100,
    mutation_rate: float = 0.01,
    elitism: int = 0,
    rng: Optional[np.random.Generator] = None,
    verbose: bool = True
) -> Tuple[np.ndarray, Dict[str, Any]]:
    if rng is None:
        rng = np.random.default_rng()
    selection_methods = ['tournament', 'roulette', 'rank']
    crossover_methods = ['one_point', 'two_point', 'uniform']
    mutation_methods = ['bit_flip', 'swap']
    results = []
    print("\n--- Iniciando busca por melhores métodos do GA ---\n")
    for sel in selection_methods:
        for cross in crossover_methods:
            for mut in mutation_methods:
                best, res = run_ga(
                    prod, cost, water, fert, price, risk,
                    budget, water_limit, fert_limit,
                    pop_size=pop_size,
                    n_gens=n_gens,
                    mutation_rate=mutation_rate,
                    selection_method=sel,
                    crossover_method=cross,
                    mutation_method=mut,
                    elitism=elitism,
                    rng=rng
                )
                results.append({
                    'best_fitness': res['best_fitness'],
                    'best': best,
                    'selection': sel,
                    'crossover': cross,
                    'mutation': mut,
                    'time_seconds': res['time_seconds'],
                    'history': res['history']
                })
                if verbose:
                    print(f"Métodos: seleção={sel}, crossover={cross}, mutação={mut}")
                    print(f"  Melhor fitness: {res['best_fitness']:.2f}")
                    print(f"  Tempo de execução: {res['time_seconds']:.2f} s\n")
    # Seleciona o melhor resultado
    best_result = max(results, key=lambda x: x['best_fitness'])
    print("--- Melhor combinação encontrada ---")
    print(f"Seleção: {best_result['selection']}, Crossover: {best_result['crossover']}, Mutação: {best_result['mutation']}")
    print(f"Melhor fitness: {best_result['best_fitness']:.2f}")
    print(f"Tempo de execução: {best_result['time_seconds']:.2f} s\n")
    return best_result['best'], best_result
