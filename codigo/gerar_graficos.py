from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


projeto = Path(__file__).resolve().parent.parent
arquivo = projeto / "dados" / "dados_selic_credito.csv"
pasta_graficos = projeto / "graficos"
pasta_graficos.mkdir(exist_ok=True)

df = pd.read_csv(arquivo, sep=";", decimal=",")
df["mes"] = pd.to_datetime(df["mes"], format="%Y-%m")

anos = pd.date_range(
    start="2015-01-01",
    end="2025-01-01",
    freq="YS"
)

plt.figure(figsize=(11, 5))
plt.plot(df["mes"], df["selic"], label="Selic")
plt.title("Evolucao da Taxa Selic - 2015 a 2025")
plt.xlabel("Periodo")
plt.ylabel("Taxa (% ao ano)")
plt.grid(alpha=0.3)
plt.legend()

ax = plt.gca()
ax.set_xlim(pd.Timestamp("2015-01-01"), pd.Timestamp("2025-12-31"))
ax.set_xticks(anos)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.savefig(pasta_graficos / "evolucao_selic.png", dpi=300)
plt.close()


modalidades = {
    "credito_pessoal": "Credito pessoal",
    "consignado": "Consignado",
    "cartao_rotativo": "Cartao rotativo",
    "capital_giro": "Capital de giro",
}

fig, eixos = plt.subplots(2, 2, figsize=(12, 8))

for eixo, (coluna, titulo) in zip(eixos.flatten(), modalidades.items()):
    eixo.plot(df["mes"], df[coluna], label=titulo)
    eixo.plot(df["mes"], df["selic"], label="Selic")
    eixo.set_title(titulo)
    eixo.set_ylabel("Taxa (% ao ano)")
    eixo.grid(alpha=0.3)
    eixo.legend()

    eixo.set_xlim(pd.Timestamp("2015-01-01"), pd.Timestamp("2025-12-31"))
    eixo.set_xticks(anos)
    eixo.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    eixo.tick_params(axis="x", rotation=45)

fig.suptitle("Selic e taxas de credito - 2015 a 2025")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(
    pasta_graficos / "comparacao_modalidades.png",
    dpi=300
)
plt.close(fig)

print("Graficos criados com sucesso!")