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


# Função para download do arquivo
def download_arquivo(uf, caminho_temp, UFs, tempo_limite, intervalo):
    try:
        url_anatel = "https://sistemas.anatel.gov.br/se/public/view/b/licenciamento.php"

        opcoes = webdriver.ChromeOptions()
        # opcoes.add_argument("--headless")  # Descomente para rodar sem abrir navegador
        opcoes.add_experimental_option("prefs", {
            "download.default_directory": caminho_temp,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        navegador = webdriver.Chrome(options=opcoes)
        navegador.get(url_anatel)

        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "filtros_adicionais")))
        navegador.find_element(By.ID, "filtros_adicionais").click()

        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "fa_gsearch")))
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

        caminho_download = verifica_download(caminho_temp, tempo_limite, intervalo)
        return caminho_download
    except Exception as error:
        print(error)
        shutil.rmtree(caminho_temp)
        return False
    finally:
        navegador.quit()


# Função para verificar se o download foi concluído com sucesso
def verifica_download(caminho_temp, tempo_limite, intervalo):
    try:
        tempo_inicio = time.time()
        while (time.time() - tempo_inicio) < tempo_limite:
            arquivo_zip = [f for f in os.listdir(caminho_temp) if f.endswith('.zip')]
            if arquivo_zip:
                print("Arquivo .zip encontrado:", arquivo_zip[0])
                caminho_completo = os.path.join(caminho_temp, arquivo_zip[0])
                return caminho_completo
            else:
                print(f"Arquivo .zip não encontrado, verificando novamente em {intervalo} segundos...")
                time.sleep(intervalo)
        print("Tempo limite alcançado. Arquivo .zip não foi encontrado.")
        return False
    except Exception as error:
        print(error)
        return False


# Função para extrair o CSV do ZIP.
def extrai_csv(caminho_zip):
    with zipfile.ZipFile(caminho_zip, 'r') as zip:
        arquivos_csv = [arquivo for arquivo in zip.namelist() if arquivo.endswith('.csv')]
        if arquivos_csv:
            arquivo_csv = arquivos_csv[0]
            with zip.open(arquivo_csv) as csv:
                return pd.read_csv(csv, encoding='latin1', on_bad_lines='skip')
        else:
            print("Não encontrado arquivo csv no zip.")
            return None


# Função para ETL do arquivo.
def processa_arquivo(arquivo, uf, UFs):
    print(f"Iniciando processamento do arquivo {UFs[uf]}.csv")

    arquivo = arquivo.astype(str).applymap(str.strip)
    arquivo.columns = arquivo.columns.str.strip()

    arquivo = arquivo[['NomeEntidade','NumFistel','NumServico','NumEstacao','SiglaUf','CodMunicipio','Tecnologia','FreqTxMHz','ClassInfraFisica','AlturaAntena','Latitude','Longitude',
                       'DataLicenciamento','DataPrimeiroLicenciamento','DataValidade','Municipio.NomeMunicipio']]

    arquivo = arquivo.rename(
        columns={
            'NomeEntidade' : "Operadora",
            'SiglaUf' : "UF",
            'FreqTxMHz' : "Frequencia",
            'ClassInfraFisica' : "TipoInfra",
            'DataLicenciamento' : "DataUltimoLicenciamento",
            'Municipio.NomeMunicipio' : "NomeMunicipio"
        }
    )

    arquivo['AlturaAntena'] = arquivo['AlturaAntena'].astype(str).str.replace('[,;]', '.', regex=True)

    arquivo['DataPrimeiroLicenciamento'] = pd.to_datetime(arquivo['DataPrimeiroLicenciamento'], errors='coerce')
    arquivo.dropna(subset=['DataPrimeiroLicenciamento'], inplace=True)

    arquivo['DataUltimoLicenciamento'] = pd.to_datetime(arquivo['DataUltimoLicenciamento'], errors='coerce')
    arquivo.dropna(subset=['DataUltimoLicenciamento'], inplace=True)

    arquivo['NumEstacao'] = pd.to_datetime(arquivo['NumEstacao'], errors='coerce')
    arquivo.dropna(subset=['NumEstacao'], inplace=True)

    arquivo = arquivo.astype({
        'Operadora': 'string',  
        'NumFistel': 'int',  
        'NumServico': 'int',  
        'UF': 'string',
        'CodMunicipio': 'int',
        'Tecnologia': 'string',
        'TipoInfra': 'string',
        'Latitude': 'float', 
        'Longitude': 'float',
        'DataUltimoLicenciamento': 'datetime64[ns]',
        'DataPrimeiroLicenciamento': 'datetime64[ns]',
        'DataValidade': 'datetime64[ns]',
        'NomeMunicipio': 'string'
    })

    arquivo['Frequencia'] = pd.to_numeric(arquivo['Frequencia'], errors='coerce')
    arquivo.dropna(subset=['Frequencia'], inplace=True)

    arquivo['AlturaAntena'] = pd.to_numeric(arquivo['AlturaAntena'], errors='coerce')
    arquivo.dropna(subset=['AlturaAntena'], inplace=True)

    arquivo = arquivo[arquivo['NumServico'] == 10]

    arquivo['TipoInfra'] = arquivo['TipoInfra'].replace('nan','Nao Especificado')

    arquivo['Operadora'] = arquivo['Operadora'].replace({
        'CLARO S.A.' : "CLARO",
        'TELEFONICA BRASIL S.A.' : "VIVO",
        'Telefonica Brasil S.a.':"VIVO",
        'TIM S A' : "TIM",
        'TIM S/A' : "TIM",
        'Brisanet Servicos de Telecomunicacoes S.A.': "BRISANET"
    })

    arquivo['Tecnologia'] = arquivo['Tecnologia'].replace({
        'GSM': "2G",
        'WCDMA': "3G",
        'WDCMA': "3G",
        'LTE': "4G",
        'NR': "5G",
        '': "Nao Informado"
    })

    arquivo['DataDownload'] = datetime.now().strftime("%d/%m/%Y")

    return arquivo


# Função para concatenar os arquivos
def concatenar_arquivos(caminho_pasta):
    print("Iniciando concatenação dos arquivos")
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
        mensagem_erro = "Nenhum arquivo csv pôde ser lido com sucesso."
        return pd.DataFrame({'Erro': [mensagem_erro]})

    df_concatenado = pd.concat(concatenado, ignore_index=True)
    print("Concatenação concluída!")
    return df_concatenado


# Definindo algumas constantes
tempo_limite = 300
intervalo = 10
UFs = ["00","AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
qtd_estados = list(range(1,28))

for uf in qtd_estados:
    caminho_temp = os.path.join(os.getcwd(), f"Mosaico - {UFs[uf]}")
    os.makedirs(caminho_temp, exist_ok=True)

    caminho_zip = download_arquivo(uf, caminho_temp, UFs, tempo_limite, intervalo)

    if caminho_zip == False:
        print(f"Erro no download da UF {UFs[uf]}.")
        shutil.rmtree(caminho_temp)
    else:
        print("Sucesso no download!")
        csv = extrai_csv(caminho_zip)
        if csv is not None:
            csv = processa_arquivo(csv, uf, UFs)
            caminho_arquivos = os.path.join(os.getcwd(), "arquivos Mosaico")
            os.makedirs(caminho_arquivos, exist_ok=True)
            csv.to_csv(os.path.join(caminho_arquivos, f"{UFs[uf]}.csv"), index=False)
        else:
            print(f"Falha ao extrair CSV da UF {UFs[uf]}.")
        shutil.rmtree(caminho_temp)

caminho_concatenado = os.path.join(os.getcwd(), "Mosaico completo")
os.makedirs(caminho_concatenado, exist_ok=True)

concatenado = concatenar_arquivos(caminho_arquivos)
concatenado.to_csv(os.path.join(caminho_concatenado, "Mosaico_Brasil.csv"), index=False)