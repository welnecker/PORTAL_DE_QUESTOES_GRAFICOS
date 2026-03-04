import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, sympify, lambdify

st.title("Gerador de Gráfico – Função por Intervalos")

st.write("Digite uma função por partes no formato:")
st.code("""
x+2 : x<0
2 : 0<=x<3
x**2-4 : x>=3
""")

entrada = st.text_area("Função", height=150)

xmin = st.number_input("x mínimo", value=-10.0)
xmax = st.number_input("x máximo", value=10.0)

if st.button("Gerar gráfico"):

    x = symbols('x')
    xs = np.linspace(xmin, xmax, 1000)
    ys = np.full_like(xs, np.nan)

    linhas = entrada.split("\n")

    try:

        for linha in linhas:
            if ":" not in linha:
                continue

            expr_str, cond_str = linha.split(":")
            expr = sympify(expr_str.strip())

            f = lambdify(x, expr, "numpy")

            cond = cond_str.strip()

            mask = eval(cond.replace("x", "xs"))

            ys[mask] = f(xs[mask])

        fig, ax = plt.subplots()

        ax.plot(xs, ys)
        ax.axhline(0)
        ax.axvline(0)

        ax.set_title("Função definida por intervalos")
        ax.grid(True)

        st.pyplot(fig)

    except Exception as e:
        st.error("Erro ao interpretar a função.")
