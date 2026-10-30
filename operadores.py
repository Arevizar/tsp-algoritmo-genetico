"""Operadores do algoritmo genético: representação, aptidão, seleção, cruzamento e mutação."""

import numpy as np


# ----------------------------------------------------------- representação

def populacao_inicial(tamanho, n_pontos, rng):
    """Primeira geração aleatória: cada indivíduo é uma permutação das cidades."""
    return np.array([rng.permutation(n_pontos) for _ in range(tamanho)])


# ----------------------------------------------------------- aptidão

def distancia_total(individuo, distancias):
    """F(I): soma das distâncias entre cidades adjacentes, fechando o ciclo."""
    seguinte = np.roll(individuo, -1)
    return distancias[individuo, seguinte].sum()


def avaliar_populacao(populacao, distancias):
    """Aplica F(I) em todos os indivíduos de uma vez."""
    seguintes = np.roll(populacao, -1, axis=1)
    return distancias[populacao, seguintes].sum(axis=1)


def aptidao(distancias_pop):
    """Quanto maior, melhor: o inverso da distância percorrida."""
    return 1.0 / distancias_pop


# ----------------------------------------------------------- seleção

def selecao_torneio(populacao, distancias_pop, n_pais, rng, k=3):
    """Sorteia k indivíduos por vaga; o de menor distância vence."""
    disputantes = rng.integers(0, len(populacao), size=(n_pais, k))
    melhor_de_cada = distancias_pop[disputantes].argmin(axis=1)
    vencedores = disputantes[np.arange(n_pais), melhor_de_cada]
    return populacao[vencedores]


def selecao_roleta(populacao, distancias_pop, n_pais, rng):
    """Amostragem estocástica: a chance de ser escolhido é proporcional à aptidão."""
    pesos = aptidao(distancias_pop)
    escolhidos = rng.choice(len(populacao), size=n_pais, p=pesos / pesos.sum())
    return populacao[escolhidos]


# ----------------------------------------------------------- cruzamento

def cruzamento_ox(pai_a, pai_b, rng):
    """Ordered Crossover: mantém um trecho de A e completa com as cidades de B, na ordem delas."""
    n = len(pai_a)
    corte1, corte2 = np.sort(rng.choice(n + 1, size=2, replace=False))
    trecho = pai_a[corte1:corte2]
    restantes = pai_b[np.isin(pai_b, trecho, invert=True)]
    filho = np.empty(n, dtype=pai_a.dtype)
    filho[corte1:corte2] = trecho
    filho[np.concatenate((np.arange(corte1), np.arange(corte2, n)))] = restantes
    return filho


# ----------------------------------------------------------- mutação

def mutacao_swap(individuo, rng):
    """Troca a posição de duas cidades."""
    i, j = rng.choice(len(individuo), size=2, replace=False)
    individuo[i], individuo[j] = individuo[j], individuo[i]
    return individuo


def mutacao_inversao(individuo, rng):
    """Inverte um trecho do caminho, trocando apenas 2 arestas do ciclo."""
    i, j = np.sort(rng.choice(len(individuo), size=2, replace=False))
    individuo[i:j + 1] = individuo[i:j + 1][::-1]
    return individuo


SELECOES = {"torneio": selecao_torneio, "roleta": selecao_roleta}
MUTACOES = {"swap": mutacao_swap, "inversao": mutacao_inversao}


if __name__ == "__main__":
    from pontos import pontos_circulares, matriz_distancias, otimo_circular

    rng = np.random.default_rng(42)
    n = 8
    distancias = matriz_distancias(pontos_circulares(n, semente=42))

    populacao = populacao_inicial(5, n, rng)
    custos = avaliar_populacao(populacao, distancias)
    print("População inicial:")
    for individuo, custo in zip(populacao, custos):
        print(" ", individuo, "->", round(custo, 1))
    print("Ótimo teórico:", round(otimo_circular(n), 2))

    filho = cruzamento_ox(populacao[0], populacao[1], rng)
    print("\nPai A:", populacao[0])
    print("Pai B:", populacao[1])
    print("Filho:", filho)
    print("Permutação válida?", sorted(filho.tolist()) == list(range(n)))

    print("\nSwap:    ", mutacao_swap(filho.copy(), rng))
    print("Inversão:", mutacao_inversao(filho.copy(), rng))