# Do Copom ao seu empréstimo: repasse da Selic ao crédito

Projeto acadêmico da disciplina de Economia e Finanças.

## Objetivo

Analisar a relação entre as variações da taxa Selic e as taxas de juros de quatro modalidades de crédito no Brasil, utilizando dados oficiais do Banco Central do Brasil entre janeiro de 2015 e dezembro de 2025.

## Tecnologias utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- Requests
- Matplotlib
- Statsmodels
- NumPy

## Funcionalidades

- Visualização interativa da evolução da Selic e das taxas de crédito.
- Seleção da modalidade de crédito e do período.
- Comparação das estimativas de repasse com intervalos de confiança.
- Apresentação dos testes de assimetria entre altas e quedas da Selic.
- Consulta e exportação dos dados históricos.

## Como executar o projeto

É necessário ter o Python e o Git instalados no computador.

### 1. Clonar o repositório

Abra o terminal do VS Code ou Git Bash e execute:

```bash
git clone https://github.com/anttonyjs/artigo-economia-financas.git
cd artigo-economia-financas
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar o ambiente virtual

No Windows, utilizando Git Bash:

```bash
source .venv/Scripts/activate
```

No Windows, utilizando PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 5. Executar o painel

```bash
python -m streamlit run app.py
```

### 6. Acessar a aplicação

Abra o endereço exibido no terminal, normalmente:

http://localhost:8501

Para encerrar a aplicação, pressione `Ctrl + C` no terminal.

## Organização do projeto

- `app.py`: aplicação principal desenvolvida com Streamlit.
- `codigo/`: scripts de coleta, tratamento dos dados e análises estatísticas.
- `dados/`: séries históricas e resultados das análises em arquivos CSV.
- `requirements.txt`: bibliotecas necessárias para executar o projeto.
- `fontes.txt`: referências das fontes de dados utilizadas.

**Observação:** para visualizar o painel, não é necessário executar separadamente os scripts da pasta `codigo/`, pois os resultados utilizados pela aplicação já estão disponíveis na pasta `dados/`.

## Fonte dos dados

Banco Central do Brasil — Sistema Gerenciador de Séries Temporais (SGS).

Séries utilizadas:

| Código SGS | Descrição |
|---|---|
| 432 | Meta da taxa Selic |
| 20742 | Crédito pessoal não consignado |
| 20747 | Crédito pessoal consignado total |
| 22022 | Cartão de crédito rotativo |
| 20725 | Capital de giro total |

Fonte: https://www3.bcb.gov.br/sgspub/

Período analisado: janeiro de 2015 a dezembro de 2025, com 132 observações mensais na base consolidada.

## Metodologia

A pesquisa utiliza dados mensais do Banco Central do Brasil.

A série diária da meta Selic foi convertida em médias mensais para permitir a comparação com as taxas de crédito.

Foram estimadas regressões por Mínimos Quadrados Ordinários (MQO), com erros-padrão robustos à heterocedasticidade e autocorrelação (HAC).

As análises incluem estimativas de repasse, testes de assimetria e verificações econométricas, como ADF, KPSS, Engle-Granger, Breusch-Godfrey e Breusch-Pagan.

Os scripts correspondentes estão disponíveis na pasta `codigo/`.

## Observações importantes

As estimativas apresentadas representam associações estatísticas entre as variações da Selic e das taxas de crédito. Os resultados não estabelecem, isoladamente, relações de causalidade.

Os filtros de período modificam os gráficos descritivos do painel, mas não recalculam as regressões estatísticas.

Os resultados devem ser interpretados considerando as limitações dos modelos utilizados.