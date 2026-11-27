
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
    df["mes"],
    format="%Y-%m"
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
    df[f"lag_{i}"] = (
        df["delta_selic"].shift(i)
    )

variaveis = [f"lag_{i}" for i in range(4)]

resultados = []

for coluna, nome in modalidades.items():

    
    df["delta_credito"] = df[coluna].diff()

    base = df[
        ["delta_credito"] + variaveis
    ].dropna()

    X = sm.add_constant(
        base[variaveis]
    )

    y = base["delta_credito"]

   
    modelo = sm.OLS(y, X).fit()

    
    bg = acorr_breusch_godfrey(
    modelo,
    nlags=4,
    result_object=False
)

   
    bp = het_breuschpagan(
        modelo.resid,
        modelo.model.exog
    )

    resultados.append({
        "modalidade": nome,
        "observacoes": int(modelo.nobs),
        "r_quadrado": modelo.rsquared,
        "p_breusch_godfrey": bg[1],
        "p_breusch_pagan": bp[1],
        "autocorrelacao_5pct": bg[1] < 0.05,
        "heterocedasticidade_5pct": bp[1] < 0.05
    })

    print(f"\nModalidade: {nome}")
    print(f"Observacoes: {int(modelo.nobs)}")
    print(f"R2: {modelo.rsquared:.4f}")
    print(f"Breusch-Godfrey p: {bg[1]:.5f}")
    print(f"Breusch-Pagan p: {bp[1]:.5f}")

tabela = pd.DataFrame(resultados)

tabela.to_csv(
    DADOS / "diagnostico_modelos.csv",
    sep=";",
    decimal=",",
    index=False,
    encoding="utf-8-sig"
)

print("\nRESUMO DOS DIAGNOSTICOS")
print(tabela.round(5).to_string(index=False))

print("\nDiagnostico finalizado!")
print("Arquivo salvo em dados/diagnostico_modelos.csv")
