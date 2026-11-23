
from pathlib import Path

import pandas as pd
from statsmodels.tsa.stattools import adfuller

# Pastas do projeto
PROJETO = Path(__file__).resolve().parent.parent
DADOS = PROJETO / "dados"

# Carregar dados do Banco Central
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

series = {
    "selic": "Selic",
    "credito_pessoal": "Credito pessoal",
    "consignado": "Consignado",
    "cartao_rotativo": "Cartao rotativo",
    "capital_giro": "Capital de giro"
}

resultados = []


def executar_adf(dados, nome, transformacao, tendencia):
    dados = dados.dropna()

    if dados.nunique() <= 1:
        raise ValueError(
            f"Serie sem variacao suficiente: {nome}"
        )

    resultado = adfuller(
    dados,
    regression=tendencia,
    autolag="AIC",
    result_object=False
)

    estatistica = resultado[0]
    p_valor = resultado[1]
    defasagens = resultado[2]
    observacoes = resultado[3]

    resultados.append({
        "serie": nome,
        "transformacao": transformacao,
        "especificacao": tendencia,
        "estatistica_adf": estatistica,
        "p_valor": p_valor,
        "defasagens": defasagens,
        "observacoes": observacoes,
        "rejeita_raiz_unitaria_5pct": p_valor < 0.05
    })


# Executar os testes
for coluna, nome in series.items():

    print(f"Analisando {nome}...")

    serie = df[coluna]

    # Serie original em nivel
    executar_adf(
        serie, nome, "Nivel", "c"
    )

    # Nivel com tendencia deterministica
    executar_adf(
        serie, nome, "Nivel", "ct"
    )

    # Primeira diferenca mensal
    primeira_diferenca = serie.diff()

    executar_adf(
        primeira_diferenca,
        nome,
        "Primeira diferenca",
        "c"
    )


# Organizar resultados
tabela = pd.DataFrame(resultados)

# Salvar resultados completos
arquivo = DADOS / "resultados_adf.csv"

tabela.to_csv(
    arquivo,
    index=False,
    sep=";",
    decimal=",",
    encoding="utf-8-sig"
)

# Exibir resumo no terminal
print("\nRESULTADOS DO TESTE ADF")
print(
    tabela.round(5).to_string(index=False)
)

print("\nINTERPRETACAO:")
print(
    "True: rejeita a hipotese de raiz "
    "unitaria ao nivel de 5%."
)
print(
    "False: nao rejeita a hipotese "
    "de raiz unitaria ao nivel de 5%."
)

print("\nTeste ADF finalizado!")
print(f"Resultados salvos em: {arquivo}")
