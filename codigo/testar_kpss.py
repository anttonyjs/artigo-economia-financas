
from pathlib import Path
import warnings

import pandas as pd
from statsmodels.tsa.stattools import kpss
from statsmodels.tools.sm_exceptions import (
    InterpolationWarning
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

series = {
    "selic": "Selic",
    "credito_pessoal": "Credito pessoal",
    "consignado": "Consignado",
    "cartao_rotativo": "Cartao rotativo",
    "capital_giro": "Capital de giro",
}

resultados = []

for coluna, nome in series.items():
    for transformacao, serie, tendencias in [
        ("Nivel", df[coluna], ["c", "ct"]),
        ("Primeira diferenca",
         df[coluna].diff(), ["c"])
    ]:
        for tendencia in tendencias:
            with warnings.catch_warnings():
                warnings.simplefilter(
                    "ignore", InterpolationWarning
                )

                estatistica, p_valor, lags, _ = kpss(
                    serie.dropna(),
                    regression=tendencia,
                    nlags="auto",
                    result_object=False
)

            resultados.append({
                "serie": nome,
                "transformacao": transformacao,
                "especificacao": tendencia,
                "estatistica_kpss": estatistica,
                "p_valor": p_valor,
                "defasagens": lags,
                "rejeita_estacionariedade_5pct":
                    p_valor < 0.05
            })

tabela = pd.DataFrame(resultados)

tabela.to_csv(
    DADOS / "resultados_kpss.csv",
    sep=";",
    decimal=",",
    index=False,
    encoding="utf-8-sig"
)

print("\nRESULTADOS DO TESTE KPSS")
print(tabela.round(5).to_string(index=False))

print("\nTrue: rejeita estacionariedade a 5%.")
print("False: nao rejeita estacionariedade a 5%.")
print(
    "Nota: valores-p do KPSS podem estar "
    "fora dos limites da tabela de referencia."
)
print("\nTeste KPSS finalizado!")
