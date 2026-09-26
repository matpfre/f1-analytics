# F1 Analytics

Pipeline de dados de Fórmula 1 de 1950 até o presente, usando o dataset
`jtrotman/formula-1-race-data` do Kaggle.

## Configuração

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

Para a coleta, configure a autenticação do Kaggle conforme a documentação da
ferramenta. Para a carga, defina `AZURE_SQL_CONNECTION_STRING` com uma URL do
SQLAlchemy compatível com `mssql+pyodbc`.

## Execução

```bash
venv/bin/python 01_collect_f1_data.py
venv/bin/python 02_clean_f1_data.py
venv/bin/python 03_load_f1_to_azure_sql.py
```

A carga falha se alguma tabela já existir. Para recriar as tabelas
explicitamente, use:

```bash
venv/bin/python 03_load_f1_to_azure_sql.py --replace
```

Todas as tabelas são lidas e validadas antes da abertura da transação de carga.
Os CSVs ficam em `data/raw/` e `data/clean/`, que não são versionados.

## Testes

```bash
venv/bin/python -m pytest -q
```