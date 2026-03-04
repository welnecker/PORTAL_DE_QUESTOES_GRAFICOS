import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, sympify, lambdify
import io

st.set_page_config(layout="wide")

st.title("Gerador de Gráficos de Funções por Intervalos")
st.write("Ferramenta para geração de gráficos didáticos para provas e listas.")

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
    xmin = st.number_input("x mínimo", value=-10.0)

with col2:
    xmax = st.number_input("x máximo", value=10.0)

col3, col4 = st.columns(2)

with col3:
    ymin = st.number_input("y mínimo", value=-10.0)

with col4:
    ymax = st.number_input("y máximo", value=10.0)


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
                continue

            expr_str, cond_str = linha.split(":")

            expr = sympify(expr_str.strip())

            f = lambdify(x, expr, "numpy")

            condicao = converter_condicao(cond_str.strip())

            mask = eval(condicao)

            ys[mask] = f(xs[mask])

        fig, ax = plt.subplots(figsize=(8,6))

        ax.plot(xs, ys, color="blue", linewidth=2)

        ax.axhline(0, color="black", linewidth=1.5)
        ax.axvline(0, color="black", linewidth=1.5)

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        ax.grid(True, linestyle="--", alpha=0.6)

        ax.set_xlabel("x")
        ax.set_ylabel("y")

        st.pyplot(fig)

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
