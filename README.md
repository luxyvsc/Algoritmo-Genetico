
# Ir Além — Algoritmo Genético para Otimização Agrícola

> Projeto de otimização de seleção de áreas agrícolas usando Algoritmo Genético (GA) com múltiplos fatores e restrições realistas do agro.

---

## Objetivo
Selecionar o melhor conjunto de áreas de plantio para maximizar o lucro, respeitando limites de orçamento, água e fertilizante, considerando risco, tipo de solo e cultura.

## Estrutura de Pastas
```
farmtech-ir-alem/
├─ data/           # Dados simulados das áreas agrícolas
├─ src/            # Código fonte do GA e utilitários
├─ configs/        # Configurações de experimentos
├─ notebooks/      # Jupyter Notebooks para análise (opcional)
├─ figures/        # Gráficos e diagramas
├─ results/        # Resultados dos experimentos
├─ requirements.txt
├─ README.md
├─ analyze_ga.py   # Script de análise completa dos resultados
└─ video_script.txt
```

## Principais Arquivos
- **src/data_generator.py**:  Gera dados sintéticos realistas para N áreas agrícolas, incluindo produtividade, custo, água (em litros), fertilizante, preço, risco, tipo de solo e cultura.
- **src/utils.py**: Lê o CSV de dados e retorna arrays para todos os atributos usados no GA.
- **src/ga_core.py**: Implementa o Algoritmo Genético com fitness multi-fator, múltiplos constraints, logging opcional e early stopping.
- **src/experiments.py**: Executa experimentos com configurações definidas em JSON, roda o GA e salva resultados em `results/`.
- **configs/baseline.json**: Exemplo de configuração de experimento, define limites de recursos e parâmetros do GA.
- **analyze_ga.py**: Script para análise completa dos resultados, estatísticas, rankings, gráficos e explicações detalhadas (fora do notebook).

## Como Funciona
1. **Geração dos Dados**
	- Execute:
	  ```powershell
	  python -m src.data_generator
	  ```
	- Gera `data/farm_data_seed42.csv` com atributos realistas para cada área.

2. **Configuração do Experimento**
	- Edite `configs/baseline.json` para definir:
	  - `budget`: orçamento máximo
	  - `water_limit`: limite de água
	  - `fert_limit`: limite de fertilizante
	  - Parâmetros do GA (população, gerações, métodos)

3. **Execução do Algoritmo Genético**
	Execute experimento:
    ```powershell
        python -m src.experiments --config configs/baseline.json
    ```
	- O GA seleciona subconjuntos de áreas maximizando receita líquida, penalizando violações de restrições.
	- Resultado salvo em `results/result_seed42.json`.

4. **Análise dos Resultados**
	 - Execute o script de análise:
		 ```powershell
		 python analyze_ga.py
		 ```
	 - O script apresenta:
		 - Estatísticas detalhadas das áreas selecionadas
		 - Ranking por produtividade e risco
		 - Penalidades aplicadas
		 - Gráficos de convergência e boxplot
		 - Apresentação explicativa dos resultados, com unidades (ex: água em litros)
		 - Textos amigáveis para facilitar interpretação
		 ```

## Modelo de Dados
Cada área agrícola tem os seguintes atributos:
- `prod`: produtividade estimada
- `cost`: custo total
- `water`: consumo de água
- `fert`: consumo de fertilizante
- `price`: preço de venda
- `risk`: índice de risco
- `soil_type`: tipo de solo
- `crop_type`: cultura

## Fitness Realista
O fitness de cada solução é calculado como:
```
fitness = receita_total - custo_total - risco_total - penalidades
```
Penalidades são aplicadas se orçamento, água ou fertilizante forem excedidos.

**O que significa o melhor fitness?**
O melhor fitness representa a qualidade da melhor solução encontrada pelo GA, considerando todos os fatores do problema (lucro, custo, risco, penalidades por exceder limites). Não é simplesmente dinheiro gasto ou área plantada, mas sim uma métrica composta que reflete o benefício agrícola total, respeitando as restrições e minimizando riscos.

## Principais Escolhas e Justificativas
- **Fitness multi-fator**: Reflete decisões reais do agro, considerando lucro, risco e sustentabilidade.
- **Múltiplos constraints**: Garante viabilidade operacional e ambiental.
- **GA flexível**: Permite testar diferentes estratégias de seleção, cruzamento e mutação.
- **Reprodutibilidade**: Uso de seed para garantir resultados consistentes.

## Como rodar do zero
1. Instale dependências:
	```powershell
	python -m pip install -r requirements.txt
	```
2. Gere dados:
	```powershell
	python -m src.data_generator
	```
3. Execute experimento:
	```powershell
	python -m src.experiments --config configs/baseline.json
	```
4. Analise resultados:
	```powershell
	python analyze_ga.py
	```
	- O script mostra todas as análises, rankings, penalidades, gráficos e explicações detalhadas.
	- Todos os valores de água são apresentados em litros para facilitar a interpretação.

## Resultados e Análise
- Resultados dos experimentos são salvos em `results/`, com nomes únicos para cada execução.
- Resultados de batch são exportados em CSV para facilitar análise e comparação.
- O script `analyze_ga.py` apresenta todas as análises relevantes, com explicações e unidades.

## Vídeo demonstrativo
## TODO: fazer o vídeo demonstrando como funciona
