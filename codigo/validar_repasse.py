
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

# Pastas do projeto
PROJETO = Path(__file__).resolve().parent.parent
DADOS = PROJETO / "dados"
GRAFICOS = PROJETO / "graficos"
GRAFICOS.mkdir(exist_ok=True)

# Carregar dados
df = pd.read_csv(
    DADOS / "dados_selic_credito.csv",
    sep=";",
    decimal=","
)

df["mes"] = pd.to_datetime(
    df["mes"], format="%Y-%m"
)
df = df.sort_values("mes").set_index("mes")

modalidades = {
    "credito_pessoal": "Credito pessoal",
    "consignado": "Consignado",
    "cartao_rotativo": "Cartao rotativo",
    "capital_giro": "Capital de giro",
}

defasagens = [0, 3, 6, 12]

# Variacoes mensais, em pontos percentuais
df["delta_selic"] = df["selic"].diff()

for atraso in range(13):
    df[f"lag_{atraso}"] = (
        df["delta_selic"].shift(atraso)
    )

# Usar a mesma amostra em todos os modelos
colunas_lags = [
    f"lag_{i}" for i in range(13)
]
base_comum = df.dropna(
    subset=colunas_lags + list(modalidades)
).copy()

resultados = []

for coluna, nome in modalidades.items():

    base_comum["delta_credito"] = (
        base_comum[coluna].diff()
    )

    # Calcular variacao na serie original,
    # antes de restringir a amostra
    y_completo = df[coluna].diff()
    y = y_completo.reindex(base_comum.index)

    for max_lag in defasagens:

        variaveis = [
            f"lag_{i}"
            for i in range(max_lag + 1)
        ]

        X = sm.add_constant(
            base_comum[variaveis]
        )

        # Erros robustos a autocorrelacao
        modelo = sm.OLS(y, X).fit(
            cov_type="HAC",
            cov_kwds={"maxlags": max(3, max_lag)}
        )

        # Testar a soma dos coeficientes
        restricao = np.zeros(len(modelo.params))

        for v in variaveis:
            posicao = modelo.params.index.get_loc(v)
            restricao[posicao] = 1

        teste = modelo.t_test(restricao)

        repasse = float(
            np.asarray(teste.effect).item()
        )

        intervalo = np.asarray(
            teste.conf_int(alpha=0.05)
        )[0]

        p_valor = float(
            np.asarray(teste.pvalue).item()
        )

        resultados.append({
            "modalidade": nome,
            "defasagens": max_lag,
            "repasse": repasse,
            "ic_inferior": float(intervalo[0]),
            "ic_superior": float(intervalo[1]),
            "p_valor": p_valor,
            "r_quadrado": modelo.rsquared,
            "observacoes": int(modelo.nobs)
        })

tabela = pd.DataFrame(resultados)

tabela.to_csv(
    DADOS / "validacao_repasse.csv",
    index=False,
    sep=";",
    decimal=",",
    encoding="utf-8-sig"
)

print("\nVALIDACAO DOS RESULTADOS")
print(tabela.round(4).to_string(index=False))


# Grafico com intervalos de confianca de 95%
grafico = tabela[
    tabela["defasagens"] == 3
].copy()

valores = grafico["repasse"].to_numpy()

erros = np.array([
    valores - grafico["ic_inferior"].to_numpy(),
    grafico["ic_superior"].to_numpy() - valores
])

fig, ax = plt.subplots(figsize=(12, 7))

# Barras das estimativas
barras = ax.bar(
    grafico["modalidade"],
    valores,
    color="#3274A1",
    width=0.60,
    label="Repasse estimado"
)

# Intervalos de confianca
ax.errorbar(
    range(len(valores)),
    valores,
    yerr=erros,
    fmt="none",
    ecolor="black",
    capsize=6,
    elinewidth=1.5,
    capthick=1.5,
    label="Intervalo de confianca de 95%"
)

# Numeros acima dos intervalos
for i, barra in enumerate(barras):
    limite = grafico.iloc[i]["ic_superior"]

    ax.annotate(
        f"{valores[i]:.2f}".replace(".", ","),
        xy=(
            barra.get_x() + barra.get_width() / 2,
            limite
        ),
        xytext=(0, 7),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )

# Titulos e identificacoes
ax.set_title(
    "Repasse estimado da Selic as taxas de credito\n"
    "Brasil - 2015 a 2025",
    fontsize=14,
    fontweight="bold",
    pad=15
)

ax.set_ylabel(
    "Pontos percentuais no credito por 1 p.p. na Selic",
    fontsize=11
)

ax.set_xlabel(
    "Modalidades de credito",
    fontsize=11
)

ax.axhline(
    0,
    color="black",
    linewidth=0.8
)

ax.grid(
    axis="y",
    alpha=0.2,
    linestyle="--"
)

ax.set_axisbelow(True)

# Legenda
ax.legend(
    loc="upper left",
    fontsize=10,
    frameon=True
)

# Espaco acima dos intervalos
maior_limite = grafico["ic_superior"].max()
ax.set_ylim(
    min(0, grafico["ic_inferior"].min() * 1.1),
    maior_limite * 1.22
)

ax.tick_params(
    axis="x",
    rotation=12,
    labelsize=10
)

# Reservar espaco para as notas
fig.subplots_adjust(
    bottom=0.27,
    top=0.88,
    left=0.10,
    right=0.97
)

# Informacoes metodologicas
fig.text(
    0.10,
    0.13,
    "Nota: Estimativas acumuladas do mes atual e "
    "tres defasagens mensais.",
    fontsize=9
)

fig.text(
    0.10,
    0.095,
    "Barras de erro: intervalos de confianca de 95%. "
    "Modelo OLS com erros robustos HAC.",
    fontsize=9
)

fig.text(
    0.10,
    0.06,
    "Fonte: Elaboracao propria com dados do "
    "Banco Central do Brasil (SGS).",
    fontsize=9
)

# Salvar imagem em alta qualidade
fig.savefig(
    GRAFICOS / "repasse_intervalos_confianca_final.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white"
)

plt.close(fig)

print("\nValidacao concluida!")
print("Grafico final salvo com sucesso!")
