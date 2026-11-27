
from pathlib import Path
from datetime import date, datetime
import pandas as pd
import requests


PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_DADOS = PASTA_PROJETO / "dados"
PASTA_DADOS.mkdir(exist_ok=True)

INICIO = "2015-01-01"
FIM = "2025-12-31"

SERIES = {
    "selic": 432,
    "credito_pessoal": 20742,
    "consignado": 20747,
    "cartao_rotativo": 22022,
    "capital_giro": 20725,
}

def buscar_serie(codigo):
    registros = []

  
    for ano in range(2015, 2026):
        inicio = f"01/01/{ano}"
        fim = f"31/12/{ano}"

        url = (
            f"https://api.bcb.gov.br/dados/serie/"
            f"bcdata.sgs.{codigo}/dados"
        )

        resposta = requests.get(
            url,
            params={
                "formato": "json",
                "dataInicial": inicio,
                "dataFinal": fim,
            },
            timeout=60,
        )
        resposta.raise_for_status()
        registros.extend(resposta.json())

    df = pd.DataFrame(registros)

    if df.empty:
        raise ValueError(f"Serie {codigo} sem dados.")

    df["data"] = pd.to_datetime(
        df["data"], format="%d/%m/%Y"
    )
    df["valor"] = pd.to_numeric(
        df["valor"].astype(str).str.replace(",", "."),
        errors="coerce",
    )

    df = df.dropna(subset=["valor"])
    df = df.drop_duplicates("data")
    return df.sort_values("data").set_index("data")

print("Iniciando coleta do Banco Central...")

dados = {}

for nome, codigo in SERIES.items():
    print(f"Baixando {nome} (SGS {codigo})...")
    dados[nome] = buscar_serie(codigo)
    dados[nome].to_csv(
        PASTA_DADOS / f"original_{nome}.csv",
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
    )


indice_diario = pd.date_range(INICIO, FIM, freq="D")
selic_diaria = (
    dados["selic"]["valor"]
    .reindex(indice_diario)
    .ffill()
)

if selic_diaria.isna().any():
    raise ValueError("Faltam valores diarios da Selic.")


selic_mensal = selic_diaria.groupby(
    selic_diaria.index.to_period("M")
).mean()
selic_mensal.name = "selic"

tabela = selic_mensal.to_frame()


for nome in SERIES:
    if nome == "selic":
        continue

    serie = dados[nome]["valor"]
    serie.index = serie.index.to_period("M")
    serie = serie.groupby(level=0).mean()
    tabela[nome] = serie


print("\nQuantidade de meses sem dados:")
print(tabela.isna().sum())

tabela.index = tabela.index.astype(str)
tabela.index.name = "mes"

arquivo = PASTA_DADOS / "dados_selic_credito.csv"
tabela.to_csv(
    arquivo,
    sep=";",
    decimal=",",
    encoding="utf-8-sig",
)

print("\nPrimeiras linhas:")
print(tabela.head())

print(f"\nArquivo salvo em: {arquivo}")
print("Coleta finalizada!")