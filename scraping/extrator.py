import zipfile
import pandas as pd

def extrai_csv(caminho_zip):
    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        arquivos_csv = [f for f in zip_ref.namelist() if f.endswith('.csv')]
        if arquivos_csv:
            with zip_ref.open(arquivos_csv[0]) as arquivo_csv:
                return pd.read_csv(arquivo_csv, encoding='latin1', on_bad_lines='skip')
        print("Nenhum arquivo CSV encontrado no ZIP.")
        return None
