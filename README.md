# Do Copom ao seu empréstimo: repasse da Selic ao crédito

Projeto acadêmico da disciplina de Economia e Finanças.

## Objetivo

Analisar a relação entre as variações da taxa Selic e as taxas de juros de quatro modalidades de crédito no Brasil, utilizando dados oficiais do Banco Central do Brasil entre janeiro de 2015 e dezembro de 2025.

## Tecnologias utilizadas

Python, Streamlit, Pandas, Plotly, Requests, Matplotlib e Statsmodels.

## Funcionalidades

- Visualização interativa da evolução da Selic e das taxas de crédito.
- Seleção da modalidade de crédito e do período.
- Comparação das estimativas de repasse com intervalos de confiança.
- Apresentação dos testes de assimetria entre altas e quedas da Selic.
- Consulta e exportação dos dados históricos.

## Como executar

É necessário ter o Python instalado.

1. Abra o terminal na pasta principal do projeto.
2. Crie e ative um ambiente virtual, se necessário.
3. Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

4. Execute o painel:

```bash
python -m streamlit run app.py
```

5. Acesse o endereço local exibido no terminal, normalmente `http://localhost:8501`.

## Fonte dos dados

Banco Central do Brasil — Sistema Gerenciador de Séries Temporais (SGS).

Séries utilizadas: 432, 20742, 20747, 22022 e 20725.

## Observações metodológicas

As estimativas apresentadas são exploratórias e representam associações estatísticas entre as variações da Selic e as taxas de crédito. Os resultados não estabelecem, isoladamente, relações de causalidade.

Os filtros de período modificam os gráficos descritivos, mas não recalculam as regressões estatísticas.