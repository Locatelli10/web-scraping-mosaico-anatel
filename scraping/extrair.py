import zipfile
import pandas as pd

# Função para extrair o CSV do ZIP.
def extrai_csv(caminho_zip):
    try:
        with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
            arquivos_csv = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            if arquivos_csv:
                with zip_ref.open(arquivos_csv[0]) as csvfile:
                    return pd.read_csv(csvfile, encoding='latin1', on_bad_lines='skip')
            else:
                print("Não encontrado arquivo CSV no zip.")
                return None
    except Exception as e:
        print("Erro ao extrair CSV:", e)
        return None
