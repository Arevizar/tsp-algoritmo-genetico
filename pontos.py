"""Cenários de pontos do caixeiro viajante e cálculo de distâncias."""

import numpy as np


def pontos_uniformes(n, largura=100.0, altura=100.0, semente=None):
    """Sorteia n pontos uniformemente dentro de um retângulo."""
    rng = np.random.default_rng(semente)
    x = rng.uniform(0.0, largura, size=n)
    y = rng.uniform(0.0, altura, size=n)
    return np.column_stack((x, y))


def pontos_circulares(n, raio=50.0, centro=(50.0, 50.0), semente=None):
    """Distribui n pontos igualmente espaçados sobre uma circunferência."""
    angulos = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    x = centro[0] + raio * np.cos(angulos)
    y = centro[1] + raio * np.sin(angulos)
    pontos = np.column_stack((x, y))
    rng = np.random.default_rng(semente)
    return rng.permutation(pontos)


def matriz_distancias(pontos):
    """Matriz n x n com a distância euclidiana entre cada par de pontos."""
    diferencas = pontos[:, np.newaxis, :] - pontos[np.newaxis, :, :]
    return np.sqrt((diferencas ** 2).sum(axis=2))


def otimo_circular(n, raio=50.0):
    """Perímetro do polígono regular de n lados: o melhor ciclo possível no círculo."""
    return n * 2.0 * raio * np.sin(np.pi / n)


if __name__ == "__main__":
    pontos = pontos_circulares(8, semente=42)
    print("Pontos do círculo:")
    print(np.round(pontos, 2))

    distancias = matriz_distancias(pontos)
    print("\nMatriz de distâncias:")
    print(np.round(distancias, 1))

    print("\nÓtimo teórico:", round(otimo_circular(8), 2))