# Web Scraping — Mosaico Anatel

Este projeto realiza web scraping no portal da **Anatel**, extraindo os dados do relatório **Mosaico**, que detalha onde operadoras de telefonia móvel possuem antenas licenciadas em todo o Brasil.

A coleta é feita de forma automatizada, estado por estado (UF), com limpeza e padronização dos dados para posterior análise.

---

# Funcionalidades

- Acesso automatizado ao sistema [Mosaico](https://sistemas.anatel.gov.br/mosaico/).
- Download dos arquivos `.csv` por Unidade da Federação (UF).
- Processamento e padronização dos dados.
- Geração de base final consolidada com informações por antena, tecnologia e município.

---
# Como Executar o Projeto

0. Clone o repositório:
   ```bash
   git clone https://github.com/leonardolima123/projeto-A3/tree/main
   cd projeto-A3
   ```

1. Crie o ambiente virtual:
   ```bash
   python -m venv .venv
   ```

2. Ative o ambiente virtual:
   - **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows**:
     ```cmd
     .venv\Scripts\activate
     ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. iniciar o Projeto:
   '''bash
   python web_scraping.py
   '''

# Tecnologias Utilizadas
Python 3.x

Selenium WebDriver

Pandas

zipfile, shutil, os, datetime

pytest (para testes)

Git + GitHub