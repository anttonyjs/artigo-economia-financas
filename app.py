
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------
# CONFIGURACAO
# -----------------------------------------

st.set_page_config(
    page_title="Do Copom ao seu Emprestimo",
    page_icon="📊",
    layout="wide"
)

PROJETO = Path(__file__).resolve().parent
DADOS = PROJETO / "dados"

MODALIDADES = {
    "Credito pessoal": "credito_pessoal",
    "Consignado": "consignado",
    "Cartao rotativo": "cartao_rotativo",
    "Capital de giro": "capital_giro",
}

NOMES_RESULTADOS = {
    "Credito pessoal": "Credito pessoal",
    "Consignado": "Consignado",
    "Cartao rotativo": "Cartao rotativo",
    "Capital de giro": "Capital de giro",
}

@st.cache_data
def carregar_csv(nome):
    caminho = DADOS / nome
    return pd.read_csv(
        caminho,
        sep=";",
        decimal=","
    )

def numero(valor):
    return f"{valor:.2f}".replace(".", ",")

# -----------------------------------------
# DADOS PRINCIPAIS
# -----------------------------------------

try:
    df = carregar_csv(
        "dados_selic_credito.csv"
    )
except (FileNotFoundError, ValueError) as erro:
    st.error(f"Erro ao carregar dados: {erro}")
    st.stop()

df["mes"] = pd.to_datetime(
    df["mes"], format="%Y-%m"
)
df = df.sort_values("mes").set_index("mes")

# -----------------------------------------
# CABECALHO
# -----------------------------------------

st.title("Do Copom ao seu empréstimo")
st.subheader("Repasse da Selic às taxas de crédito")

st.write(
    "Painel de análise econômica com dados do "
    "Banco Central do Brasil, de janeiro de 2015 "
    "a dezembro de 2025."
)

col1, col2, col3 = st.columns(3)

col1.metric("Meses na base", len(df))
col2.metric("Séries históricas", 5)
col3.metric("Modalidades de crédito", 4)

st.divider()

# -----------------------------------------
# FILTROS
# -----------------------------------------

st.sidebar.header("Filtros")

modalidade = st.sidebar.selectbox(
    "Modalidade de crédito",
    list(MODALIDADES.keys())
)

ano_inicial, ano_final = st.sidebar.slider(
    "Período dos gráficos",
    min_value=2015,
    max_value=2025,
    value=(2015, 2025)
)

coluna = MODALIDADES[modalidade]

filtrado = df[
    (df.index.year >= ano_inicial)
    & (df.index.year <= ano_final)
]

# -----------------------------------------
# EVOLUCAO DAS TAXAS
# -----------------------------------------

st.header("1. Evolução das taxas de juros")

c1, c2 = st.columns(2)

c1.metric(
    "Selic - último mês selecionado",
    f"{numero(filtrado['selic'].iloc[-1])}%"
)

c2.metric(
    f"{modalidade} - último mês",
    f"{numero(filtrado[coluna].iloc[-1])}%"
)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=filtrado.index,
    y=filtrado["selic"],
    mode="lines",
    name="Selic",
    line=dict(color="#E69F00", width=3),
    hovertemplate="%{x|%m/%Y}: %{y:.2f}%<extra></extra>"
))

fig.add_trace(go.Scatter(
    x=filtrado.index,
    y=filtrado[coluna],
    mode="lines",
    name=modalidade,
    line=dict(color="#3274A1", width=3),
    hovertemplate="%{x|%m/%Y}: %{y:.2f}%<extra></extra>"
))

fig.update_layout(
    title=f"Selic x {modalidade}",
    xaxis_title="Período",
    yaxis_title="Taxa (% ao ano)",
    hovermode="x unified",
    height=420,
    margin=dict(l=20, r=20, t=55, b=20),
    xaxis=dict(
        range=[
            filtrado.index.min(),
            filtrado.index.max()
        ]
        
    )
)

st.plotly_chart(
    fig, width="stretch"
)

st.caption(
    "Fonte: Banco Central do Brasil (SGS). "
    "Taxas expressas em percentual ao ano."
)

st.divider()

# -----------------------------------------
# ESTIMATIVAS DO REPASSE
# -----------------------------------------

st.header("2. Repasse estimado da Selic")

st.write(
    "Estimativas de associação entre as variações "
    "mensais da Selic e as taxas de crédito. "
    "Foram consideradas três defasagens mensais."
)

try:
    repasse = carregar_csv(
        "validacao_repasse.csv"
    )
except (FileNotFoundError, ValueError):
    st.warning(
        "Arquivo validacao_repasse.csv nao encontrado."
    )
else:
    repasse = repasse[
        repasse["defasagens"] == 3
    ].copy()

    repasse["erro_inferior"] = (
        repasse["repasse"] - repasse["ic_inferior"]
    )
    repasse["erro_superior"] = (
        repasse["ic_superior"] - repasse["repasse"]
    )

    fig_repasse = go.Figure()

    fig_repasse.add_trace(go.Bar(
        x=repasse["modalidade"],
        y=repasse["repasse"],
        marker_color="#3274A1",
        text=[
            numero(v) for v in repasse["repasse"]
        ],
        textposition="outside",
        error_y=dict(
            type="data",
            symmetric=False,
            array=repasse["erro_superior"],
            arrayminus=repasse["erro_inferior"],
            visible=True
        ),
        name="Repasse estimado"
    ))

    fig_repasse.update_layout(
        title="Repasse e intervalos de confiança de 95%",
        yaxis_title=(
            "Pontos percentuais no crédito "
            "por 1 p.p. na Selic"
        ),
        height=450,
        margin=dict(l=20, r=20, t=60, b=40)
    )

    st.plotly_chart(
        fig_repasse, width="stretch"
    )

    st.caption(
        "Estimativas para 2015-2025, com 119 "
        "observações por modalidade. "
        "Os coeficientes não comprovam causalidade. "
        "O filtro de anos acima não recalcula "
        "estas regressões."
    )

    with st.expander("Ver resultados detalhados"):
        colunas = [
            "modalidade",
            "repasse",
            "ic_inferior",
            "ic_superior",
            "p_valor",
            "r_quadrado",
            "observacoes"
        ]
        st.dataframe(
            repasse[colunas].round(4),
            hide_index=True
        )

st.divider()

# -----------------------------------------
# ASSIMETRIA
# -----------------------------------------

st.header("3. Análise de assimetria")

st.write(
    "Comparação entre as respostas estimadas "
    "às altas e às quedas da Selic. "
    "Os resultados variam conforme a especificação "
    "estatística utilizada."
)

try:
    assimetria = carregar_csv(
        "validacao_assimetria.csv"
    )
except (FileNotFoundError, ValueError):
    st.warning(
        "Arquivo validacao_assimetria.csv "
        "nao encontrado."
    )
else:
    resumo = assimetria.pivot(
        index="modalidade",
        columns="defasagens",
        values="p_assimetria"
    )

    resumo.columns = [
        f"{col} defasagens"
        for col in resumo.columns
    ]

    st.dataframe(
        resumo.round(4),
        width="stretch"
    )

    st.info(
        "Valores-p abaixo de 0,05 indicam "
        "evidência estatística de diferença "
        "entre os coeficientes de altas e quedas, "
        "nas condições do modelo. "
        "A significância não se manteve "
        "em todas as especificações."
    )

st.divider()

# -----------------------------------------
# DADOS E METODOLOGIA
# -----------------------------------------

st.header("4. Dados e metodologia")

st.write(
    "Fonte: Sistema Gerenciador de Séries "
    "Temporais (SGS) do Banco Central do Brasil."
)

st.write(
    "A meta Selic diária foi transformada em "
    "média mensal. Foram analisadas quatro "
    "modalidades de crédito com taxas anuais."
)

st.write(
    "A análise utilizou regressões por mínimos "
    "quadrados ordinários (MQO), erros-padrão "
    "robustos HAC e testes de sensibilidade."
)

with st.expander("Consultar base mensal"):
    st.dataframe(
        filtrado.round(3),
        width="stretch"
    )

with st.expander("Limitações da pesquisa"):
    st.write(
        "As estimativas representam associações "
        "estatísticas e não comprovam causalidade. "
        "Fatores como risco de crédito, inflação, "
        "inadimplência e mudanças na composição "
        "das operações podem influenciar os juros."
    )
    st.write(
        "Os resultados do cartão rotativo "
        "apresentaram maior incerteza e problemas "
        "nos diagnósticos de alguns modelos."
    )

# -----------------------------------------
# DOWNLOAD
# -----------------------------------------

st.subheader("Baixar dados")

csv = df.reset_index().to_csv(
    index=False,
    sep=";",
    decimal=","
).encode("utf-8-sig")

st.download_button(
    label="Baixar base histórica em CSV",
    data=csv,
    file_name="dados_selic_credito.csv",
    mime="text/csv"
)

st.divider()

st.caption(
    "Projeto acadêmico de Economia e Finanças | "
    "Dados: Banco Central do Brasil (SGS) | "
    "Período: 2015-2025."
)