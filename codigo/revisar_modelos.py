
from pathlib import Path

import pandas as pd
import statsmodels.api as sm

from statsmodels.stats.diagnostic import (
    acorr_breusch_godfrey,
    het_breuschpagan
)

PROJETO = Path(__file__).resolve().parent.parent
DADOS = PROJETO / "dados"

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

df["delta_selic"] = df["selic"].diff()

for i in range(4):
    df[f"selic_lag{i}"] = (
        df["delta_selic"].shift(i)
    )

resultados = []

for coluna, nome in modalidades.items():

    df["delta_credito"] = df[coluna].diff()

    df["credito_anterior"] = (
        df["delta_credito"].shift(1)
    )

    variaveis = (
        [f"selic_lag{i}" for i in range(4)]
        + ["credito_anterior"]
    )

    base = df[
        ["delta_credito"] + variaveis
    ].dropna()

    X = sm.add_constant(base[variaveis])
    y = base["delta_credito"]

    modelo = sm.OLS(y, X).fit(
        cov_type="HAC",
        cov_kwds={"maxlags": 4}
    )

    bg = acorr_breusch_godfrey(
        modelo,
        nlags=4,
        result_object=False
    )

    bp = het_breuschpagan(
        modelo.resid,
        modelo.model.exog,
        robust=True
    )

    resultados.append({
        "modalidade": nome,
        "observacoes": int(modelo.nobs),
        "r_quadrado": modelo.rsquared,
        "coef_credito_anterior":
            modelo.params["credito_anterior"],
        "p_breusch_godfrey": bg[1],
        "p_breusch_pagan": bp[1],
    })

    # Salvar relatorio individual
    with open(
        DADOS / f"modelo_revisado_{coluna}.txt",
        "w",
        encoding="utf-8"
    ) as arquivo:
        arquivo.write(modelo.summary().as_text())

tabela = pd.DataFrame(resultados)

tabela.to_csv(
    DADOS / "diagnostico_modelos_revisados.csv",
    index=False,
    sep=";",
    decimal=",",
    encoding="utf-8-sig"
)

print("\nDIAGNOSTICO DOS MODELOS REVISADOS")
print(tabela.round(5).to_string(index=False))

print("\nRevisao finalizada!")
