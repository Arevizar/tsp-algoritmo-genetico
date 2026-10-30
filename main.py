import sys
from pathlib import Path

import matplotlib.pyplot as plt

from ga import evoluir
from pontos import (
    matriz_distancias,
    otimo_circular,
    pontos_circulares,
    pontos_uniformes,
)
from visual import animar, figura_epocas, figura_resultado

SEMENTE = 42
PASTA = Path("figuras")


def relatar(nome, resultado, otimo=None):
    print(f"\n===== {nome} =====")
    print("Parada:          ", resultado["motivo_parada"])
    print("Épocas:          ", resultado["epocas"])
    print("Tempo:            %.2f s" % resultado["tempo"])
    print("Melhor distância: %.2f" % resultado["melhor_distancia"])
    if otimo is not None:
        print("Ótimo teórico:    %.2f" % otimo)
        print("Acima do ótimo:   %.2f%%" % (100 * abs(resultado["melhor_distancia"] / otimo - 1)))


def epocas_amostradas(resultado, quantidade=5):
    ultima = resultado["epocas"] - 1
    return sorted({round(i * ultima / (quantidade - 1)) for i in range(quantidade)})


def cenario_uniforme(n=30):
    pontos = pontos_uniformes(n, semente=SEMENTE)
    resultado = evoluir(
        matriz_distancias(pontos),
        tamanho_populacao=100,
        max_epocas=800,
        paciencia=150,
        semente=SEMENTE,
    )
    relatar(f"Uniforme com {n} pontos", resultado)
    plt.close(figura_resultado(pontos, resultado, None,
                               f"Uniforme com {n} pontos", PASTA / "uniforme.png"))
    plt.close(figura_epocas(pontos, resultado, epocas_amostradas(resultado),
                            "Uniforme: melhor rota ao longo das épocas",
                            PASTA / "uniforme_epocas.png"))
    return animar(pontos, resultado)


def cenario_circular(n=30):
    pontos = pontos_circulares(n, semente=SEMENTE)
    otimo = otimo_circular(n)
    resultado = evoluir(
        matriz_distancias(pontos),
        tamanho_populacao=100,
        max_epocas=800,
        paciencia=150,
        meta=otimo * 1.001,
        semente=SEMENTE,
    )
    relatar(f"Circular com {n} pontos", resultado, otimo)
    plt.close(figura_resultado(pontos, resultado, otimo,
                               f"Círculo com {n} pontos", PASTA / "circular.png"))
    plt.close(figura_epocas(pontos, resultado, epocas_amostradas(resultado),
                            "Círculo: melhor rota ao longo das épocas",
                            PASTA / "circular_epocas.png"))
    return animar(pontos, resultado, otimo)


CENARIOS = {"uniforme": cenario_uniforme, "circular": cenario_circular}


if __name__ == "__main__":
    PASTA.mkdir(exist_ok=True)
    escolhidos = sys.argv[1:] or list(CENARIOS)
    for nome in escolhidos:
        animacao = CENARIOS[nome]()
        plt.show()