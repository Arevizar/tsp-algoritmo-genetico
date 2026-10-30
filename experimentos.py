import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ga import evoluir
from main import epocas_amostradas
from pontos import (
    matriz_distancias,
    otimo_circular,
    pontos_circulares,
    pontos_uniformes,
)
from visual import animar, figura_epocas

SEMENTE = 42
PASTA = Path("figuras")
REPETICOES = 5
ORCAMENTO = dict(max_epocas=400, paciencia=400)


def padronizar(curvas):
    comprimento = max(len(c) for c in curvas)
    return np.array([np.pad(c, (0, comprimento - len(c)), mode="edge") for c in curvas])


def media_de_execucoes(distancias, **parametros):
    finais = []
    curvas = []
    for i in range(REPETICOES):
        resultado = evoluir(distancias, semente=SEMENTE + i, **parametros)
        finais.append(resultado["melhor_distancia"])
        curvas.append(resultado["historico_melhor"])
    return np.mean(finais), np.std(finais), padronizar(curvas).mean(axis=0)


def comparar(distancias, variantes, titulo, arquivo):
    print(f"\n===== {titulo} =====")
    figura, eixo = plt.subplots(figsize=(7.5, 4.5), layout="constrained")
    for rotulo, parametros in variantes.items():
        media, desvio, curva = media_de_execucoes(distancias, **ORCAMENTO, **parametros)
        print(f"{rotulo:>12}: {media:7.2f} +- {desvio:5.2f}")
        eixo.plot(curva, label=f"{rotulo} — {media:.1f}")
    eixo.set_xlabel("época")
    eixo.set_ylabel(f"melhor distância (média de {REPETICOES} execuções)")
    eixo.legend()
    eixo.grid(alpha=0.3)
    figura.suptitle(titulo)
    figura.savefig(arquivo, dpi=150)
    return figura


def experimento_populacao(n=30):
    distancias = matriz_distancias(pontos_uniformes(n, semente=SEMENTE))
    tamanhos = [20, 50, 100, 150, 300]
    medias = []
    desvios = []
    tempos = []

    print("\n===== Tamanho da população =====")
    figura, (eixo_curvas, eixo_custo) = plt.subplots(
        1, 2, figsize=(12, 4.5), layout="constrained"
    )
    for tamanho in tamanhos:
        finais = []
        curvas = []
        duracoes = []
        for i in range(REPETICOES):
            resultado = evoluir(distancias, tamanho_populacao=tamanho,
                                semente=SEMENTE + i, **ORCAMENTO)
            finais.append(resultado["melhor_distancia"])
            curvas.append(resultado["historico_melhor"])
            duracoes.append(resultado["tempo"])
        media = np.mean(finais)
        desvio = np.std(finais)
        medias.append(media)
        desvios.append(desvio)
        tempos.append(np.mean(duracoes))
        print(f"{tamanho:>5}: {media:7.2f} +- {desvio:5.2f}  ({np.mean(duracoes):.2f} s)")
        eixo_curvas.plot(padronizar(curvas).mean(axis=0), label=str(tamanho))

    eixo_curvas.set_xlabel("época")
    eixo_curvas.set_ylabel("melhor distância")
    eixo_curvas.legend(fontsize=8, title="população")
    eixo_curvas.grid(alpha=0.3)

    eixo_custo.errorbar(tamanhos, medias, yerr=desvios, marker="o", capsize=4)
    eixo_custo.set_xlabel("tamanho da população")
    eixo_custo.set_ylabel("distância final")
    eixo_custo.grid(alpha=0.3)

    gemeo = eixo_custo.twinx()
    gemeo.plot(tamanhos, tempos, color="tab:red", marker="s", linestyle=":")
    gemeo.set_ylabel("tempo por execução (s)", color="tab:red")

    figura.suptitle("Escolha do tamanho da população")
    figura.savefig(PASTA / "populacao.png", dpi=150)
    return figura


def experimento_mutacao(n=30):
    distancias = matriz_distancias(pontos_uniformes(n, semente=SEMENTE))
    taxas = [0.0, 0.05, 0.1, 0.2, 0.4, 0.8]
    medias = []
    desvios = []

    print("\n===== Taxa de mutação =====")
    figura, (eixo_curvas, eixo_final) = plt.subplots(
        1, 2, figsize=(12, 4.5), layout="constrained"
    )
    for taxa in taxas:
        media, desvio, curva = media_de_execucoes(distancias, taxa_mutacao=taxa, **ORCAMENTO)
        print(f"{taxa:>6.0%}: {media:7.2f} +- {desvio:5.2f}")
        medias.append(media)
        desvios.append(desvio)
        eixo_curvas.plot(curva, label=f"{taxa:.0%}")

    eixo_curvas.set_xlabel("época")
    eixo_curvas.set_ylabel("melhor distância")
    eixo_curvas.legend(fontsize=8)
    eixo_curvas.grid(alpha=0.3)

    eixo_final.errorbar([t * 100 for t in taxas], medias, yerr=desvios,
                        marker="o", capsize=4, color="tab:blue")
    eixo_final.set_xlabel("taxa de mutação (%)")
    eixo_final.set_ylabel("distância final")
    eixo_final.grid(alpha=0.3)

    figura.suptitle("Escolha da taxa de mutação")
    figura.savefig(PASTA / "taxa_mutacao.png", dpi=150)
    return figura


def experimento_operadores(n=30):
    distancias = matriz_distancias(pontos_uniformes(n, semente=SEMENTE))
    return comparar(
        distancias,
        {"swap": {"mutacao": "swap"}, "inversão": {"mutacao": "inversao"}},
        "Mutação: swap vs inversão",
        PASTA / "mutacao_operador.png",
    )


def experimento_selecao(n=30):
    distancias = matriz_distancias(pontos_uniformes(n, semente=SEMENTE))
    return comparar(
        distancias,
        {"torneio": {"selecao": "torneio"}, "roleta": {"selecao": "roleta"}},
        "Seleção: torneio vs roleta",
        PASTA / "selecao.png",
    )


def bonus(n=100):
    pontos = pontos_circulares(n, semente=SEMENTE)
    otimo = otimo_circular(n)
    resultado = evoluir(
        matriz_distancias(pontos),
        tamanho_populacao=300,
        max_epocas=3000,
        paciencia=400,
        meta=otimo * 1.01,
        semente=SEMENTE,
    )
    print(f"\n===== Bônus: círculo com {n} pontos =====")
    print("Parada:          ", resultado["motivo_parada"])
    print("Épocas:          ", resultado["epocas"])
    print("Tempo total:      %.1f s" % resultado["tempo"])
    print("Tempo por época:  %.1f ms" % (1000 * resultado["tempo"] / resultado["epocas"]))
    print("Melhor distância: %.2f" % resultado["melhor_distancia"])
    print("Ótimo teórico:    %.2f" % otimo)
    print("Acima do ótimo:   %.2f%%" % (100 * (resultado["melhor_distancia"] / otimo - 1)))
    plt.close(figura_epocas(pontos, resultado, epocas_amostradas(resultado, 6),
                            f"Bônus: círculo com {n} pontos",
                            PASTA / "bonus_epocas.png"))
    return animar(pontos, resultado, otimo)


EXPERIMENTOS = {
    "populacao": experimento_populacao,
    "mutacao": experimento_mutacao,
    "operadores": experimento_operadores,
    "selecao": experimento_selecao,
    "bonus": bonus,
}


if __name__ == "__main__":
    PASTA.mkdir(exist_ok=True)
    guardados = []
    for nome in sys.argv[1:] or list(EXPERIMENTOS):
        guardados.append(EXPERIMENTOS[nome]())
        plt.show()