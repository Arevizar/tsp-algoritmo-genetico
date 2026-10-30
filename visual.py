import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


def desenhar_rota(eixo, pontos, caminho, titulo=""):
    
    ordem = np.append(caminho, caminho[0])
    eixo.plot(pontos[ordem, 0], pontos[ordem, 1], "-", linewidth=1.2, color="tab:blue")
    eixo.plot(pontos[:, 0], pontos[:, 1], "o", markersize=5, color="tab:red")
    eixo.set_title(titulo, fontsize=10)
    eixo.set_aspect("equal")
    eixo.set_xticks([])
    eixo.set_yticks([])


def desenhar_convergencia(eixo, resultado, otimo=None):
    
    eixo.plot(resultado["historico_melhor"], color="tab:blue", label="melhor")
    eixo.plot(resultado["historico_media"], color="tab:orange", alpha=0.7, label="média da população")
    if otimo is not None:
        eixo.axhline(otimo, linestyle="--", color="tab:green", label="ótimo teórico")
    eixo.set_xlabel("época")
    eixo.set_ylabel("distância")
    eixo.legend(fontsize=8)
    eixo.grid(alpha=0.3)


def figura_resultado(pontos, resultado, otimo=None, titulo="", arquivo=None):
    
    figura, (eixo_rota, eixo_curva) = plt.subplots(
        1, 2, figsize=(11, 4.5), layout="constrained", width_ratios=[1, 1.4]
    )
    desenhar_rota(eixo_rota, pontos, resultado["melhor_caminho"],
                  f"distância {resultado['melhor_distancia']:.2f}")
    desenhar_convergencia(eixo_curva, resultado, otimo)
    figura.suptitle(titulo)
    if arquivo:
        figura.savefig(arquivo, dpi=150)
    return figura


def figura_epocas(pontos, resultado, epocas, titulo="", arquivo=None):
   
    figura, eixos = plt.subplots(1, len(epocas), figsize=(3.2 * len(epocas), 3.6))
    for eixo, epoca in zip(np.atleast_1d(eixos), epocas):
        indice = min(epoca, resultado["epocas"] - 1)
        desenhar_rota(eixo, pontos, resultado["caminhos"][indice],
                      f"época {indice}\n{resultado['historico_melhor'][indice]:.1f}")
    figura.suptitle(titulo)
    figura.tight_layout()
    if arquivo:
        figura.savefig(arquivo, dpi=150)
    return figura


def animar(pontos, resultado, otimo=None, intervalo=40, max_quadros=200, arquivo=None):
    figura, (eixo_rota, eixo_curva) = plt.subplots(
        1, 2, figsize=(11, 4.5), layout="constrained", width_ratios=[1, 1.4]
    )
    desenhar_convergencia(eixo_curva, resultado, otimo)
    marcador = eixo_curva.axvline(0, color="tab:red", linewidth=1)
    figura.canvas.draw()
    figura.set_layout_engine("none")

    passo = max(1, resultado["epocas"] // max_quadros)
    quadros = list(range(0, resultado["epocas"], passo))

    def quadro(epoca):
        eixo_rota.clear()
        desenhar_rota(eixo_rota, pontos, resultado["caminhos"][epoca],
                      f"época {epoca} — distância {resultado['historico_melhor'][epoca]:.2f}")
        marcador.set_xdata([epoca, epoca])
        return ()

    animacao = FuncAnimation(figura, quadro, frames=quadros,
                             interval=intervalo, repeat=False)
    if arquivo:
        animacao.save(arquivo, writer="pillow", fps=max(1, 1000 // intervalo))
    return animacao


if __name__ == "__main__":
    from ga import evoluir
    from pontos import matriz_distancias, otimo_circular, pontos_circulares

    n = 20
    pontos = pontos_circulares(n, semente=3)
    otimo = otimo_circular(n)
    resultado = evoluir(matriz_distancias(pontos), meta=otimo * 1.001, semente=3)

    print(resultado["motivo_parada"], "|", resultado["epocas"], "épocas")
    figura_resultado(pontos, resultado, otimo, f"Círculo com {n} pontos")
    animacao = animar(pontos, resultado, otimo)
    plt.show()