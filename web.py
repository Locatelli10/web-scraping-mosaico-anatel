import os
import shutil
from scraping.download import download_arquivo
from scraping.extrair import extract_and_load_csv_from_zip
from scraping.concatenador import concatenar_arquivos
from processamento.processador_dados_anatel import ProcessadorDadosAnatel

# Definindo algumas constantes
tempo_limite = 300
intervalo = 10
UFs = ["00","AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG",
       "MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
qtd_estados = list(range(1, 3))#28))

caminho_arquivos = os.path.join(os.getcwd(), "arquivos Mosaico")
os.makedirs(caminho_arquivos, exist_ok=True)

processador = ProcessadorDadosAnatel()

# Iniciando nossos downloads
for uf in qtd_estados:
    caminho_temp = os.path.join(os.getcwd(), f"Mosaico - {UFs[uf]}")
    os.makedirs(caminho_temp, exist_ok=True)

    caminho_zip = download_arquivo(uf, caminho_temp, UFs, tempo_limite, intervalo)
    if not caminho_zip:
        print(f"Erro no download da UF {UFs[uf]}.")
        shutil.rmtree(caminho_temp, ignore_errors=True)
        continue

    print("Sucesso no download!")
    csv = extract_and_load_csv_from_zip(caminho_zip)
    if csv is not None:
        df = processador.processar(csv)
        df.to_csv(os.path.join(caminho_arquivos, f"{UFs[uf]}.csv"), index=False)
        print(f"Arquivo {UFs[uf]}.csv salvo com sucesso.")
    else:
        print(f"Falha ao extrair CSV da UF {UFs[uf]}.")

    shutil.rmtree(caminho_temp, ignore_errors=True)

# Criando pasta para armazenar um arquivo completo com todas as UFs.
caminho_concatenado = os.path.join(os.getcwd(), "Mosaico completo")
os.makedirs(caminho_concatenado, exist_ok=True)
# Concatenando os arquivos
df_concat = concatenar_arquivos(caminho_arquivos)

# Verifica se a concatenação foi bem-sucedida e se o DataFrame não está vazio
if df_concat is not None and not df_concat.empty:
    df_concat.to_csv(os.path.join(caminho_concatenado, "Mosaico_Brasil.csv"), index=False)
    print("Arquivo Mosaico_Brasil.csv criado com sucesso!")
else:
    print("Nenhum dado válido foi concatenado.")
