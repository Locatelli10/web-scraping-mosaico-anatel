import os
import shutil
import time
import zipfile
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime

# ✅ Importando o processador refatorado
from processador_dados_anatel import ProcessadorDadosAnatel

# Instanciando o processador
processador = ProcessadorDadosAnatel()

# Função para download do arquivo
def download_arquivo(uf):
    try:
        # Definindo a url a ser acessada
        url_anatel = "https://sistemas.anatel.gov.br/se/public/view/b/licenciamento.php"

        # criando uma instancia do chrome_options
        opcoes = webdriver.ChromeOptions()
        #opcoes.add_argument("--headless") # Argumento para baixar em segundo plano
        opcoes.add_experimental_option("prefs", {
            "download.default_directory": caminho_temp,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        
        navegador = webdriver.Chrome(options=opcoes)
        # Abrindo url no navegador
        navegador.get(url_anatel)

        
        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "filtros_adicionais")))
        
        navegador.find_element(By.ID, "filtros_adicionais").click()

        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "fa_gsearch")))
        # Abrindo dropdown "Search by" e selecionando filtro por estado (UF)
        Select(navegador.find_element(By.ID, "fa_gsearch")).select_by_index(1)

        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "fa_uf")))
        
        Select(navegador.find_element(By.ID, "fa_uf")).select_by_value(f"{UFs[uf]}")

        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "import")))
        
        navegador.find_element(By.ID, "import").click()

        WebDriverWait(navegador, 60).until(EC.invisibility_of_element_located((By.ID, "wait_box")))
        
        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "download_csv")))

        time.sleep(2)
        
        navegador.find_element(By.ID, "download_csv").click()

        WebDriverWait(navegador, 60).until(EC.invisibility_of_element_located((By.ID, "wait_box")))
        # A partir desse ponto vamos presumir que o download tenha iniciado. Agora vamos monitorar a pasta destino para saber se o download foi um sucesso.


        caminho_dowload = verifica_download(caminho_temp, tempo_limite, intervalo)
        
        return caminho_dowload
    except Exception as error:
    
        print(error)
        shutil.rmtree(caminho_temp)
        return False
    finally:
    
        navegador.quit()

# Função para verificar se o download foi concluído
def verifica_download(caminho_temp, tempo_limite, intervalo):
    try:
        # Obtendo a hora de inicio da verificação
        tempo_inicio = time.time()
        
        while (time.time() - tempo_inicio) < tempo_limite:
            # Obtendo os arquivos .zip contidos na pasta
            arquivo_zip = [f for f in os.listdir(caminho_temp) if f.endswith('.zip')]
        
            if arquivo_zip:
                print("Arquivo .zip encontrado:", arquivo_zip[0])
                return os.path.join(caminho_temp, arquivo_zip[0])
            else:
                print("Arquivo .zip não encontrado, verificando novamente em 5 segundos...")
                time.sleep(intervalo)
       
        print("Tempo limite alcançado. Arquivo .zip não foi encontrado.")
        return False
    except Exception as error:
        
        print(error)

# Função para extrair o CSV do ZIP
def extrai_csv(caminho_zip):
    # Abrindo ZIP
    with zipfile.ZipFile(caminho_zip, 'r') as zip:
        # Buscando por arquivos CSV
        arquivos_csv = [arquivo for arquivo in zip.namelist() if arquivo.endswith('.csv')]
    
        if arquivos_csv:
            with zip.open(arquivos_csv[0]) as csv:
                return pd.read_csv(csv, encoding='latin1', on_bad_lines='skip')
        else:
            print("Não encontrado arquivo csv no zip.")

# Função para concatenar os arquivos
def concatenar_arquivos(caminho_pasta):
    print(f"Iniciando concatenação dos arquivos")
    # Criando variável concatenado para receber os dados
    concatenado = []
    
    for arquivo in os.listdir(caminho_pasta):
        if arquivo.endswith(".csv"):
            caminho_completo = os.path.join(caminho_pasta, arquivo)
            try:
                df_temp = pd.read_csv(caminho_completo)
                concatenado.append(df_temp)
            except Exception as e:
                print(f"Erro ao ler '{arquivo}': {e}. Este arquivo será ignorado.")

    if not concatenado:
        return pd.DataFrame({'Erro': ["Nenhum arquivo csv pôde ser lido com sucesso."]})

    df_concatenado = pd.concat(concatenado, ignore_index=True)
    print("Concatenação concluída!")
    return df_concatenado

# Definindo algumas constantes
# Tempo limite para conclusão do download
tempo_limite = 300
# Intervalo entre cada verificação do download
intervalo = 10
# Criando lista com as unidades federativas
UFs = ["00","AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
qtd_estados = list(range(1, 28))

# Iniciando nossos downloads
for uf in qtd_estados:
    # Criando pasta temporária para receber o download
    caminho_temp = os.path.join(os.getcwd(), f"Mosaico - {UFs[uf]}")
    os.makedirs(caminho_temp, exist_ok=True)
    # Iniciando download
    caminho_zip = download_arquivo(uf)

    if not caminho_zip:
        print(f"Erro no download da UF {UFs[uf]}.")
        shutil.rmtree(caminho_temp)
    else:
        print("Sucesso no download!")
        csv = extrai_csv(caminho_zip)

        # ✅ Processando usando a classe refatorada
        csv = processador.processar(csv)

        caminho_arquivos = os.path.join(os.getcwd(), "arquivos Mosaico")
        os.makedirs(caminho_arquivos, exist_ok=True)
        csv.to_csv(os.path.join(f"{caminho_arquivos}\\{UFs[uf]}.csv"), index=False)

        shutil.rmtree(caminho_temp)

# Concatenando todos os arquivos
caminho_concatenado = os.path.join(os.getcwd(), "Mosaico completo")
os.makedirs(caminho_concatenado, exist_ok=True)
concatenado = concatenar_arquivos(caminho_arquivos)
concatenado.to_csv(os.path.join(f"{caminho_concatenado}\\Mosaico_Brasil.csv"), index=False)