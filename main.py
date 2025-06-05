import os
import tempfile
from scraping.downloader import download_arquivo
from scraping.extrator import extrai_csv
from scraping.concatenador import concatenar_csvs
from processamento.processador_dados_anatel import ProcessadorDadosAnatel

UFs = ["00","AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
qtd_estados = list(range(1, 28))
tempo_limite = 300
intervalo = 10

processador = ProcessadorDadosAnatel()
pasta_final = "dados_csv"

os.makedirs(pasta_final, exist_ok=True)

for uf in qtd_estados:
    print(f"Baixando dados da UF: {UFs[uf]}")
    with tempfile.TemporaryDirectory() as caminho_temp:
        zip_path = download_arquivo(uf, caminho_temp, tempo_limite, intervalo, UFs)
        if not zip_path:
            continue
        df = extrai_csv(zip_path)
        if df is not None:
            df_processado = processador.processar(df)
            df_processado.to_csv(f"{pasta_final}/{UFs[uf]}.csv", index=False)

# Opcional: consolidar
df_consolidado = concatenar_csvs(pasta_final)
df_consolidado.to_csv("dados_consolidados.csv", index=False)
print("Processamento finalizado.")

