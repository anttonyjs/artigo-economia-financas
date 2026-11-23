
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

# Ler a base de dados
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

# Separar movimentos da Selic
delta_selic = df["selic"].diff()

df["alta"] = delta_selic.clip(lower=0)
df["queda"] = delta_selic.clip(upper=0)

# Gerar ate 12 defasagens
for i in range(13):
    df[f"alta_{i}"] = df["alta"].shift(i)
    df[f"queda_{i}"] = df["queda"].shift(i)

# Variacoes das taxas de credito
for coluna in modalidades:
    df[f"delta_{coluna}"] = df[coluna].diff()

    # Variacao do mes anterior
    df[f"anterior_{coluna}"] = (
        df[f"delta_{coluna}"].shift(1)
    )

# Comparar modelos na mesma amostra
todas_variaveis = (
    [f"alta_{i}" for i in range(13)]
    + [f"queda_{i}" for i in range(13)]
    + [f"delta_{c}" for c in modalidades]
    + [f"anterior_{c}" for c in modalidades]
)

base_comum = df.dropna(
    subset=todas_variaveis
).copy()

print(
    "Observacoes na amostra comum:",
    len(base_comum)
)

resultados = []

for coluna, nome in modalidades.items():

    y = base_comum[f"delta_{coluna}"]

    for max_lag in [3, 6, 12]:

        altas = [
            f"alta_{i}"
            for i in range(max_lag + 1)
        ]

        quedas = [
            f"queda_{i}"
            for i in range(max_lag + 1)
        ]

        anterior = f"anterior_{coluna}"
        variaveis = altas + quedas + [anterior]

        X = sm.add_constant(
            base_comum[variaveis]
        )

        modelo = sm.OLS(y, X).fit(
            cov_type="HAC",
            cov_kwds={
                "maxlags": max(3, max_lag)
            }
        )

        def vetor_contraste(nomes):
            vetor = np.zeros(
                len(modelo.params)
            )

            for variavel in nomes:
                indice = (
                    modelo.params.index.get_loc(
                        variavel
                    )
                )
                vetor[indice] = 1

            return vetor

        vetor_alta = vetor_contraste(altas)
        vetor_queda = vetor_contraste(quedas)

        teste_alta = modelo.t_test(vetor_alta)
        teste_queda = modelo.t_test(vetor_queda)

        # Hipotese: repasse de alta = repasse de queda
        teste_diferenca = modelo.t_test(
            vetor_alta - vetor_queda
        )

        def valor_teste(teste):
            return float(
                np.asarray(teste.effect).item()
            )

        resultados.append({
            "modalidade": nome,
            "defasagens": max_lag,
            "repasse_alta": valor_teste(
                teste_alta
            ),
            "repasse_queda": valor_teste(
                teste_queda
            ),
            "diferenca": valor_teste(
                teste_diferenca
            ),
            "p_assimetria": float(
                np.asarray(
                    teste_diferenca.pvalue
                ).item()
            ),
            "r_quadrado": modelo.rsquared,
            "observacoes": int(modelo.nobs)
        })

# Consolidar resultados
tabela = pd.DataFrame(resultados)

tabela["significativo_5pct"] = (
    tabela["p_assimetria"] < 0.05
)

tabela.to_csv(
    DADOS / "validacao_assimetria.csv",
    sep=";",
    decimal=",",
    index=False,
    encoding="utf-8-sig"
)

print("\nVALIDACAO DA ASSIMETRIA")
print(
    tabela.round(4).to_string(index=False)
)

# Grafico da diferenca entre repasses
fig, eixos = plt.subplots(
    2, 2, figsize=(12, 8)
)

for eixo, (nome, grupo) in zip(
    eixos.flatten(),
    tabela.groupby("modalidade", sort=False)
):

    eixo.plot(
        grupo["defasagens"],
        grupo["diferenca"],
        marker="o",
        linewidth=2
    )

    eixo.axhline(
        0,
        color="black",
        linestyle="--",
        linewidth=1
    )

    for _, linha in grupo.iterrows():
        eixo.annotate(
            f'{linha["diferenca"]:.2f}',
            (
                linha["defasagens"],
                linha["diferenca"]
            ),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=9
        )

    eixo.set_title(nome)
    eixo.set_xticks([3, 6, 12])
    eixo.set_xlabel(
        "Numero de defasagens mensais"
    )
    eixo.set_ylabel(
        "Diferenca: alta menos queda"
    )
    eixo.grid(alpha=0.25)

fig.suptitle(
    "Robustez da assimetria do repasse da Selic\n"
    "Brasil - 2015 a 2025",
    fontsize=14,
    fontweight="bold"
)

fig.tight_layout(
    rect=[0, 0.08, 1, 0.93]
)

fig.text(
    0.08, 0.035,
    "Nota: Diferenca entre coeficientes "
    "acumulados de altas e quedas. "
    "Modelo com variacao anterior do credito.",
    fontsize=9
)

fig.text(
    0.08, 0.015,
    "Fonte: Elaboracao propria com dados "
    "do Banco Central do Brasil (SGS).",
    fontsize=9
)

fig.savefig(
    GRAFICOS / "robustez_assimetria.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white"
)

plt.close(fig)

print("\nValidacao finalizada!")
print("Arquivos gerados com sucesso.")
