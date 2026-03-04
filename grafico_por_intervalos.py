import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, sympify, lambdify
import io

st.set_page_config(layout="wide")

st.title("Gerador de Gráficos de Funções por Intervalos")
st.write("Ferramenta para professores gerarem gráficos para provas e listas.")

st.markdown("### Formato da função")

st.code("""
x+2 : x<0
2 : 0<=x<3
x**2-4 : x>=3
""")

entrada = st.text_area("Função definida por intervalos", height=150)

st.markdown("### Janela do gráfico")

col1, col2 = st.columns(2)

with col1:
    xmin = st.number_input("x mínimo", value=-5.0)

with col2:
    xmax = st.number_input("x máximo", value=5.0)

col3, col4 = st.columns(2)

with col3:
    ymin = st.number_input("y mínimo", value=-5.0)

with col4:
    ymax = st.number_input("y máximo", value=5.0)


def converter_condicao(cond):

    cond = cond.replace(" ", "")

    if "<=" in cond and "<" in cond and cond.count("<") == 2:
        a, b, c = cond.replace("<=", "<=").split("<")
        return f"(xs>={a}) & (xs<{c})"

    if "<=" in cond and cond.count("<=") == 2:
        a, b, c = cond.split("<=")
        return f"(xs>={a}) & (xs<={c})"

    cond = cond.replace("x", "xs")

    return cond


if st.button("Gerar gráfico"):

    x = symbols('x')

    xs = np.linspace(xmin, xmax, 2000)

    ys = np.full_like(xs, np.nan)

    linhas = entrada.split("\n")

    try:

        for linha in linhas:

            if ":" not in linha:

                expr = sympify(linha.strip())
                f = lambdify(x, expr, "numpy")
                ys = f(xs)
            
                break
            expr_str, cond_str = linha.split(":")

            expr = sympify(expr_str.strip())

            f = lambdify(x, expr, "numpy")

            condicao = converter_condicao(cond_str.strip())

            mask = eval(condicao)

            ys[mask] = f(xs[mask])

        fig, ax = plt.subplots(figsize=(5,4))

        # gráfico da função
        ax.plot(xs, ys, color="blue", linewidth=2)

        # limites
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        # escala matemática perfeita
        ax.set_aspect('equal', adjustable='box')

        # mover eixos para origem
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')

        # esconder bordas superiores
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')

        # espessura dos eixos
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_linewidth(1.2)

        # marcações inteiras
        xticks = np.arange(xmin, xmax+1, 1)
        yticks = np.arange(ymin, ymax+1, 1)

        # remover o 0 duplicado
        xticks = xticks[xticks != 0]
        yticks = yticks[yticks != 0]

        ax.set_xticks(xticks)
        ax.set_yticks(yticks)

        # números menores
        ax.tick_params(
            axis='both',
            which='major',
            labelsize=6,
            length=3,
            width=0.8,
            pad=2
        )

        ax.tick_params(
            axis='both',
            which='minor',
            length=2,
            width=0.5
        )

        # grade estilo livro
        ax.minorticks_on()

        ax.grid(True, which='major', linestyle='-', linewidth=0.6, alpha=0.7)
        ax.grid(True, which='minor', linestyle=':', linewidth=0.4, alpha=0.5)

        # setas nos eixos
        ax.plot((1), (0), ls="", marker=">", ms=6, color="black",
                transform=ax.get_yaxis_transform(), clip_on=False)

        ax.plot((0), (1), ls="", marker="^", ms=6, color="black",
                transform=ax.get_xaxis_transform(), clip_on=False)

        # centralizar gráfico
        colA, colB, colC = st.columns([1,2,1])

        with colB:
            st.pyplot(fig)

        # exportar PNG
        buffer = io.BytesIO()

        fig.savefig(buffer, format="png", dpi=300, bbox_inches="tight")

        st.download_button(
            label="Baixar gráfico (PNG 300dpi)",
            data=buffer.getvalue(),
            file_name="grafico_funcao.png",
            mime="image/png"
        )

    except Exception as e:

        st.error(f"Erro ao interpretar a função: {e}")
