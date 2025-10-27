
---

## ⚡ Funcionalidades

1. **Coleta de Dados**
   - Autenticação via **JWT** na API Pokémon.
   - Obtenção de:
     - Lista de Pokémons
     - Atributos detalhados de cada Pokémon
     - Dados de combates
   - Armazenamento em arquivos CSV na pasta `out/`.

2. **Processamento e Limpeza**
   - Conversão de tipos de dados.
   - Remoção de registros duplicados.
   - Inserção dos dados limpos em um banco PostgreSQL.
   - Criação de tabelas auxiliares:
     - `pokemons`
     - `atributos_pokemon`
     - `combates`
     - `estatisticas_pokemon`
     - `top10_vitorias` e `top10_derrotas`
     - `comparativo_atributos_top10`

3. **Dashboard Interativo**
   - Visualização das **Top 10 vitórias** e **Top 10 derrotas**.
   - Comparativo de atributos entre os **Top 10 Pokémon** e a **média geral**.
   - Gráficos interativos:
     - Barras agrupadas para atributos
     - Radar comparativo
   - Tabelas com destaque condicional para diferenças de atributos.

4. **Geração de Dashboard HTML**
   - Criação de dashboard standalone em `report/dashboard_pokemon_estilizado.html`.

---

## 🛠 Tecnologias Utilizadas

- **Python 3.11+**
- **Pandas** - manipulação de dados
- **Requests** - consumo da API Pokémon
- **SQLAlchemy + psycopg2** - integração com PostgreSQL
- **Plotly** - visualização interativa de gráficos
- **Streamlit** - dashboard interativo
- **Dotenv** - gerenciamento de variáveis de ambiente

---

## ⚙️ Configuração do Ambiente

1. Clone o repositório:

```bash
git clone https://github.com/Carlos-Dev-br/projeto_kaizen.git
cd projeto_kaizen


## ⚙️ Execução
```python
pip install -r requirements.txt
python src/main.py
python python -m streamlit run dashboard/dashboard.py
