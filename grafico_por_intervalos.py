import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, sympify, lambdify
import pandas as pd
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


# ---------------------------------------------------
# PAINEL DE ESTILO
# ---------------------------------------------------

st.markdown("### Estilo do gráfico")

c1, c2 = st.columns(2)

with c1:
    cor_funcao = st.color_picker("Cor da função", "#1f77b4")
    espessura_funcao = st.slider("Espessura da função", 1.0, 5.0, 2.0)

with c2:
    estilo_linha = st.selectbox(
        "Estilo da linha",
        ["Sólida", "Tracejada", "Pontilhada"]
    )

    cor_grade = st.color_picker("Cor da grade", "#b0b0b0")

mapa_estilo = {
    "Sólida": "-",
    "Tracejada": "--",
    "Pontilhada": ":"
}

st.markdown("### Estilo dos eixos")

c3, c4 = st.columns(2)

with c3:
    cor_eixos = st.color_picker("Cor dos eixos", "#000000")

with c4:
    espessura_eixos = st.slider("Espessura dos eixos", 0.5, 3.0, 1.2)


# ---------------------------------------------------
# FUNÇÃO PARA INTERVALOS
# ---------------------------------------------------

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


# ---------------------------------------------------
# GERAR GRÁFICO
# ---------------------------------------------------

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

        ax.plot(
            xs,
            ys,
            color=cor_funcao,
            linewidth=espessura_funcao,
            linestyle=mapa_estilo[estilo_linha]
        )

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        ax.set_aspect('equal', adjustable='box')

        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')

        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')

        ax.spines['left'].set_linewidth(espessura_eixos)
        ax.spines['bottom'].set_linewidth(espessura_eixos)

        ax.spines['left'].set_color(cor_eixos)
        ax.spines['bottom'].set_color(cor_eixos)

        xticks = np.arange(xmin, xmax+1, 1)
        yticks = np.arange(ymin, ymax+1, 1)

        xticks = xticks[xticks != 0]
        yticks = yticks[yticks != 0]

        ax.set_xticks(xticks)
        ax.set_yticks(yticks)

        ax.tick_params(
            axis='both',
            which='major',
            labelsize=6,
            length=3,
            width=0.8,
            pad=2
        )

        ax.grid(True, which='major', linestyle='-', linewidth=0.6, color=cor_grade, alpha=0.7)

        ax.plot((1), (0), ls="", marker=">", ms=6, color=cor_eixos,
                transform=ax.get_yaxis_transform(), clip_on=False)

        ax.plot((0), (1), ls="", marker="^", ms=6, color=cor_eixos,
                transform=ax.get_xaxis_transform(), clip_on=False)

        ax.text(xmax, 0.2, "x", fontsize=9, ha="right")
        ax.text(0.2, ymax, "y", fontsize=9, va="top")

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

        # ---------------------------------------------------
        # TABELA DE VALORES DO GRÁFICO
        # ---------------------------------------------------

        st.markdown("### Tabela de valores da função")

        xs_tabela = np.arange(xmin, xmax + 1, 1)

        ys_tabela = []

        for valor in xs_tabela:

            try:
                y_val = np.interp(valor, xs, ys)
                ys_tabela.append(round(y_val, 4))
            except:
                ys_tabela.append(None)

        tabela = pd.DataFrame({
            "x": xs_tabela,
            "f(x)": ys_tabela
        })

        st.dataframe(tabela, use_container_width=True)

    except Exception as e:

        st.error(f"Erro ao interpretar a função: {e}")
