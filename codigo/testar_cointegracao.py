
from pathlib import Path
import pandas as pd
from statsmodels.tsa.stattools import coint

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
    "cartao_rotativo": "Cartao rotativo"
}

resultados = []

for coluna, nome in modalidades.items():

    base = df[["selic", coluna]].dropna()

    estatistica, p_valor, valores_criticos = coint(
        base[coluna],
        base["selic"],
        trend="c",
        autolag="aic"
    )

    resultados.append({
        "modalidade": nome,
        "estatistica": estatistica,
        "p_valor": p_valor,
        "critico_5pct": valores_criticos[1],
        "rejeita_sem_cointegracao_5pct":
            p_valor < 0.05,
        "observacoes": len(base)
    })

tabela = pd.DataFrame(resultados)

print("\nTESTE DE COINTEGRACAO")
print(tabela.round(5).to_string(index=False))

tabela.to_csv(
    DADOS / "resultados_cointegracao.csv",
    sep=";",
    decimal=",",
    index=False,
    encoding="utf-8-sig"
)

print("\nTeste concluido!")
print("Resultados salvos com sucesso.")
