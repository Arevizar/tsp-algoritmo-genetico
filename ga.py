"""Loop evolutivo do algoritmo genético e critérios de parada."""

import time
from functools import partial

import numpy as np

from operadores import (
    MUTACOES,
    SELECOES,
    avaliar_populacao,
    cruzamento_ox,
    populacao_inicial,
)


def evoluir(
    distancias,
    tamanho_populacao=100,
    max_epocas=500,
    taxa_mutacao=0.2,
    elitismo=2,
    selecao="torneio",
    mutacao="inversao",
    k_torneio=3,
    paciencia=100,
    meta=None,
    semente=None,
):
    """Roda o algoritmo genético e devolve a melhor solução e o histórico de cada época."""
    rng = np.random.default_rng(semente)
    n_pontos = len(distancias)

    selecionar = SELECOES[selecao]
    if selecao == "torneio":
        selecionar = partial(selecionar, k=k_torneio)
    mutar = MUTACOES[mutacao]

    populacao = populacao_inicial(tamanho_populacao, n_pontos, rng)
    custos = avaliar_populacao(populacao, distancias)

    melhor_caminho = populacao[custos.argmin()].copy()
    melhor_custo = custos.min()
    epocas_sem_ganho = 0

    historico_melhor = []
    historico_media = []
    caminhos = []
    motivo = f"limite de {max_epocas} épocas"
    inicio = time.perf_counter()

    for _ in range(max_epocas):
        historico_melhor.append(melhor_custo)
        historico_media.append(custos.mean())
        caminhos.append(melhor_caminho.copy())

        if meta is not None and melhor_custo <= meta:
            motivo = f"meta de {meta:.2f} atingida"
            break
        if epocas_sem_ganho >= paciencia:
            motivo = f"{paciencia} épocas sem ganho"
            break

        elite = populacao[np.argsort(custos)[:elitismo]]
        n_filhos = tamanho_populacao - elitismo

        pais_a = selecionar(populacao, custos, n_filhos, rng)
        pais_b = selecionar(populacao, custos, n_filhos, rng)

        filhos = np.empty((n_filhos, n_pontos), dtype=populacao.dtype)
        for i in range(n_filhos):
            filho = cruzamento_ox(pais_a[i], pais_b[i], rng)
            if rng.random() < taxa_mutacao:
                filho = mutar(filho, rng)
            filhos[i] = filho

        populacao = np.vstack((elite, filhos))
        custos = avaliar_populacao(populacao, distancias)

        if custos.min() < melhor_custo - 1e-9:
            melhor_custo = custos.min()
            melhor_caminho = populacao[custos.argmin()].copy()
            epocas_sem_ganho = 0
        else:
            epocas_sem_ganho += 1

    return {
        "melhor_caminho": melhor_caminho,
        "melhor_distancia": melhor_custo,
        "historico_melhor": np.array(historico_melhor),
        "historico_media": np.array(historico_media),
        "caminhos": caminhos,
        "epocas": len(historico_melhor),
        "tempo": time.perf_counter() - inicio,
        "motivo_parada": motivo,
    }


if __name__ == "__main__":
    from pontos import matriz_distancias, otimo_circular, pontos_circulares

    n = 12
    distancias = matriz_distancias(pontos_circulares(n, semente=7))
    otimo = otimo_circular(n)

    resultado = evoluir(distancias, meta=otimo * 1.001, semente=7)

    print("Motivo da parada:", resultado["motivo_parada"])
    print("Épocas:", resultado["epocas"])
    print("Tempo: %.3f s" % resultado["tempo"])
    print("Melhor distância:", round(resultado["melhor_distancia"], 2))
    print("Ótimo teórico:   ", round(otimo, 2))
    print("Acima do ótimo: %.2f%%" % (100 * (resultado["melhor_distancia"] / otimo - 1)))
    print("Caminho:", resultado["melhor_caminho"])