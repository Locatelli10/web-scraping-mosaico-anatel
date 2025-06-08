# Web Scraping — Mosaico Anatel

Este projeto realiza web scraping no portal da **Anatel**, extraindo os dados do relatório **Mosaico**, que detalha onde operadoras de telefonia móvel possuem antenas licenciadas em todo o Brasil.

A coleta é feita de forma automatizada, estado por estado (UF), com limpeza e padronização dos dados para posterior análise.

---

## Funcionalidades

- Acesso automatizado ao sistema [Mosaico](https://sistemas.anatel.gov.br/mosaico/) via **Selenium**.
- Download dos arquivos `.csv` por Unidade da Federação (UF).
- Extração dos dados de arquivos `.zip`.
- Processamento e padronização dos dados com **Pandas**.
- Geração de base final consolidada com informações por antena, tecnologia e município.

---

## Como Executar o Projeto

### 1. Clone o repositório
```bash
git clone https://github.com/leonardolima123/projeto-A3
cd projeto-A3
```

### 2. Crie o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ative o ambiente virtual

* **Linux/macOS**:

  ```bash
  source .venv/bin/activate
  ```
* **Windows**:

  ```cmd
  .venv\Scripts\activate
  ```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Execute o script principal

```bash
python web.py
```

---
## Como executar os testes

### 1. Para executar o arquivo *test_funcoes_processador.py*

```bash
python -m unittest test_funcoes_processador.py
```

## Estrutura

```
projeto
├── scraping/
    **download.py      
    **extrair.py    
    **concatenador.py
├── processamento/processador_dados_anatel.py
├── web.py  #Script principal
├── requirements.txt
└── README.md
```

---

## Tecnologias Utilizadas

* **Python 3.x**
* **Selenium WebDriver**
* **Pandas**
* **zipfile**, **shutil**, **os**, **datetime**
* **pytest**
* **Git + GitHub**

---

## Observações

* Os dados são baixados diretamente do sistema público da Anatel.
* A coleta pode demorar alguns minutos dependendo da conexão e do número de estados processados.
* Ao final da execução, é gerado um arquivo consolidado `Mosaico_Brasil.csv` na pasta `Mosaico completo/`.

```
