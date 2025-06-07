import os
import pandas as pd

# Função para concatenar os arquivos
def concatenar_arquivos(caminho_pasta):
    print(f"Iniciando concatenação dos arquivos na pasta '{caminho_pasta}'")
    dfs = []
    if not os.path.exists(caminho_pasta):
        print(f"A pasta '{caminho_pasta}' não existe.")
        return None

    for arquivo in os.listdir(caminho_pasta):
        if arquivo.endswith(".csv"):
            try:
                df = pd.read_csv(os.path.join(caminho_pasta, arquivo))
                dfs.append(df)
            except Exception as e:
                print(f"Erro ao ler '{arquivo}': {e}")

    if not dfs:
        print("Nenhum arquivo CSV pôde ser lido.")
        return None

    return pd.concat(dfs, ignore_index=True)
