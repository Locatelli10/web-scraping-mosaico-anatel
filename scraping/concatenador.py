import os
import pandas as pd

def concatenar_csvs(caminho_pasta):
    dados = []
    for arquivo in os.listdir(caminho_pasta):
        if arquivo.endswith(".csv"):
            try:
                df = pd.read_csv(os.path.join(caminho_pasta, arquivo))
                dados.append(df)
            except Exception as e:
                print(f"Erro ao ler {arquivo}: {e}")
    if not dados:
        return pd.DataFrame({'Erro': ["Nenhum CSV lido com sucesso."]})
    return pd.concat(dados, ignore_index=True)
