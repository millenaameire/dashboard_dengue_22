# Dengue no Brasil (2022–2025): MongoDB Atlas + Python

Análise dos casos de dengue no Brasil entre 2022 e 2025, usando **MongoDB Atlas** como banco de dados, **Python** para consulta e **Streamlit** para o dashboard interativo.

Projeto da disciplina **Banco de Dados Não Relacional**

## 🎯 O que o projeto faz

1. **Coleta** os dados de dengue do SINAN (Ministério da Saúde) de 2022 a 2025 e agrega por **município × ano**.
2. Gera um arquivo **JSON** e **importa no MongoDB Atlas**.
3. Consulta o banco com *aggregation pipelines*:
   - soma de casos por **região**;
   - **média de casos por estado** em cada região;
   - casos em **10 grandes cidades da região Sul**.
4. Mostra tudo em **mapas (folium)**, **gráfico (plotly)** e em um **dashboard Streamlit**.

## 📊 Resultado: média de casos por estado, por região (2022–2025)

| Região | Média por estado | Estados |
|---|---:|---:|
| Sudeste | 1.698.420 | 4 |
| Sul | 708.744 | 3 |
| Centro-Oeste | 341.676 | 4 |
| Nordeste | 88.095 | 9 |
| Norte | 25.674 | 7 |

## ▶️ Como executar

### 1. Banco de dados (MongoDB Atlas)
1. Crie um cluster gratuito (M0) no [MongoDB Atlas](https://cloud.mongodb.com).
2. Em **Database Access**, crie um usuário e senha.
3. Em **Network Access**, libere o acesso (`0.0.0.0/0` para uso acadêmico).

### 2. Notebook no Google Colab
1. Abra `Dengue_MongoDB_Atlas.ipynb` no [Google Colab](https://colab.research.google.com).
2. Execute **Ambiente de execução → Executar tudo**.
3. Quando solicitado, informe o usuário, a senha e o host do seu cluster.

### 3. Dashboard Streamlit
```bash
pip install -r requirements.txt

# PowerShell (Windows)
$env:MONGO_URI="mongodb+srv://USUARIO:SENHA@SEU_CLUSTER.mongodb.net/"

# Prompt de Comando (cmd)
set "MONGO_URI=mongodb+srv://USUARIO:SENHA@SEU_CLUSTER.mongodb.net/"

# Linux / macOS
export MONGO_URI="mongodb+srv://USUARIO:SENHA@SEU_CLUSTER.mongodb.net/"

streamlit run app.py
```

## 📚 Fonte dos dados

- **Ministério da Saúde, SINAN** (Sistema de Informação de Agravos de Notificação), Dengue 2022–2025, via [OpenDataSUS](https://opendatasus.saude.gov.br/dataset/arboviroses-dengue).
- Nomes dos municípios: [API de localidades do IBGE](https://servicodados.ibge.gov.br/api/v1/localidades/municipios).


## 🛠️ Tecnologias

Python · MongoDB Atlas · PyMongo · Pandas · Folium · Plotly · Streamlit · Google Colab

## 👩‍💻 Autora

**Millena Meireles** · [GitHub](https://github.com/millenaameire)
