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

# Função para verificar se o download foi concluído com sucesso
def verifica_download(caminho_temp, tempo_limite, intervalo):
    try:
        tempo_inicio = time.time()
        while (time.time() - tempo_inicio) < tempo_limite:
            arquivos_zip = [f for f in os.listdir(caminho_temp) if f.endswith('.zip')]
            if arquivos_zip:
                print("Arquivo .zip encontrado:", arquivos_zip[0])
                caminho_completo = os.path.join(caminho_temp, arquivos_zip[0])
                return caminho_completo
            else:
                print(f"Arquivo .zip não encontrado, verificando novamente em {intervalo} segundos...")
                time.sleep(intervalo)
        print("Tempo limite alcançado. Arquivo .zip não foi encontrado.")
        return False
    except Exception as error:
        print("Erro na verificação de download:", error)
        return False


# Função para download do arquivo
def download_arquivo(uf, caminho_temp, UFs, tempo_limite, intervalo):
    try:
        url_anatel = "https://sistemas.anatel.gov.br/se/public/view/b/licenciamento.php"

        opcoes = webdriver.ChromeOptions()
        #opcoes.add_argument("--headless")  # Descomente para rodar sem abrir navegador

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
        time.sleep(2)  # Dá tempo para o botão ficar clicável

        navegador.find_element(By.ID, "download_csv").click()

        WebDriverWait(navegador, 60).until(EC.invisibility_of_element_located((By.ID, "wait_box")))

        caminho_download = verifica_download(caminho_temp, tempo_limite, intervalo)
        return caminho_download
    except Exception as error:
        print("Erro no download:", error)
        shutil.rmtree(caminho_temp, ignore_errors=True)
        return False
    finally:
        try:
            navegador.quit()
        except:
            pass


# Função para extrair o CSV do ZIP.
def extrai_csv(caminho_zip):
    try:
        with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
            arquivos_csv = [arquivo for arquivo in zip_ref.namelist() if arquivo.endswith('.csv')]
            if arquivos_csv:
                arquivo_csv = arquivos_csv[0]
                with zip_ref.open(arquivo_csv) as csvfile:
                    return pd.read_csv(csvfile, encoding='latin1', on_bad_lines='skip')
            else:
                print("Não encontrado arquivo csv no zip.")
                return None
    except Exception as e:
        print("Erro ao extrair CSV do ZIP:", e)
        return None


# Função para processar o arquivo CSV
def processa_arquivo(df, uf, UFs):
    print(f"Iniciando processamento do arquivo {UFs[uf]}.csv")

    df = df.astype(str).applymap(str.strip)
    df.columns = df.columns.str.strip()

    colunas_necessarias = ['NomeEntidade','NumFistel','NumServico','NumEstacao','SiglaUf',
                          'CodMunicipio','Tecnologia','FreqTxMHz','ClassInfraFisica','AlturaAntena',
                          'Latitude','Longitude','DataLicenciamento','DataPrimeiroLicenciamento',
                          'DataValidade','Municipio.NomeMunicipio']

    df = df[colunas_necessarias]

    df = df.rename(
        columns={
            'NomeEntidade' : "Operadora",
            'SiglaUf' : "UF",
            'FreqTxMHz' : "Frequencia",
            'ClassInfraFisica' : "TipoInfra",
            'DataLicenciamento' : "DataUltimoLicenciamento",
            'Municipio.NomeMunicipio' : "NomeMunicipio"
        }
    )

    df['AlturaAntena'] = df['AlturaAntena'].str.replace('[,;]', '.', regex=True)

    df['DataPrimeiroLicenciamento'] = pd.to_datetime(df['DataPrimeiroLicenciamento'], errors='coerce')
    df.dropna(subset=['DataPrimeiroLicenciamento'], inplace=True)

    df['DataUltimoLicenciamento'] = pd.to_datetime(df['DataUltimoLicenciamento'], errors='coerce')
    df.dropna(subset=['DataUltimoLicenciamento'], inplace=True)

    # Parece que houve confusão aqui, 'NumEstacao' não parece data, talvez int?
    df['NumEstacao'] = pd.to_numeric(df['NumEstacao'], errors='coerce')
    df.dropna(subset=['NumEstacao'], inplace=True)

    df = df.astype({
        'Operadora': 'string',  
        'NumFistel': 'int64',  
        'NumServico': 'int64',  
        'UF': 'string',
        'CodMunicipio': 'int64',
        'Tecnologia': 'string',
        'TipoInfra': 'string',
        'Latitude': 'float64', 
        'Longitude': 'float64',
        'DataUltimoLicenciamento': 'datetime64[ns]',
        'DataPrimeiroLicenciamento': 'datetime64[ns]',
        'DataValidade': 'datetime64[ns]',
        'NomeMunicipio': 'string'
    })

    df['Frequencia'] = pd.to_numeric(df['Frequencia'], errors='coerce')
    df.dropna(subset=['Frequencia'], inplace=True)

    df['AlturaAntena'] = pd.to_numeric(df['AlturaAntena'], errors='coerce')
    df.dropna(subset=['AlturaAntena'], inplace=True)

    df = df[df['NumServico'] == 10]

    df['TipoInfra'] = df['TipoInfra'].replace('nan','Nao Especificado')

    df['Operadora'] = df['Operadora'].replace({
        'CLARO S.A.' : "CLARO",
        'TELEFONICA BRASIL S.A.' : "VIVO",
        'Telefonica Brasil S.a.':"VIVO",
        'TIM S A' : "TIM",
        'TIM S/A' : "TIM",
        'Brisanet Servicos de Telecomunicacoes S.A.': "BRISANET"
    })

    df['Tecnologia'] = df['Tecnologia'].replace({
        'GSM': "2G",
        'WCDMA': "3G",
        'WDCMA': "3G",
        'LTE': "4G",
        'NR': "5G",
        '': "Nao Informado"
    })

    df['DataDownload'] = datetime.now().strftime("%d/%m/%Y")

    return df


# Função para concatenar os arquivos CSV da pasta
def concatenar_arquivos(caminho_pasta):
    print(f"Iniciando concatenação dos arquivos na pasta '{caminho_pasta}'")
    concatenado = []

    if not os.path.exists(caminho_pasta): 
        print(f"A pasta '{caminho_pasta}' não existe.")
        return None

    for arquivo in os.listdir(caminho_pasta):
        if arquivo.endswith(".csv"):
            caminho_completo = os.path.join(caminho_pasta, arquivo)
            try:
                df_temp = pd.read_csv(caminho_completo)
                concatenado.append(df_temp)
            except Exception as e:
                print(f"Erro ao ler '{arquivo}': {e}. Este arquivo será ignorado.")

    if not concatenado:
        print("Nenhum arquivo csv pôde ser lido com sucesso.")
        return None

    df_concatenado = pd.concat(concatenado, ignore_index=True)
    print("Concatenação concluída!")
    return df_concatenado


# Parâmetros principais
tempo_limite = 300
intervalo = 10
UFs = ["00","AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG",
       "MS","MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
qtd_estados = list(range(1, 28))  # 1 a 27 para acessar UFs corretamente

# Pasta para salvar arquivos processados
caminho_arquivos = os.path.join(os.getcwd(), "arquivos Mosaico")
os.makedirs(caminho_arquivos, exist_ok=True)

for uf in qtd_estados:
    caminho_temp = os.path.join(os.getcwd(), f"Mosaico - {UFs[uf]}")
    os.makedirs(caminho_temp, exist_ok=True)

    caminho_zip = download_arquivo(uf, caminho_temp, UFs, tempo_limite, intervalo)

    if caminho_zip == False:
        print(f"Erro no download da UF {UFs[uf]}.")
        shutil.rmtree(caminho_temp, ignore_errors=True)
        continue

    print("Sucesso no download!")

    csv = extrai_csv(caminho_zip)
    if csv is not None:
        csv = processa_arquivo(csv, uf, UFs)
        csv.to_csv(os.path.join(caminho_arquivos, f"{UFs[uf]}.csv"), index=False)
        print(f"Arquivo {UFs[uf]}.csv salvo com sucesso.")
    else:
        print(f"Falha ao extrair CSV da UF {UFs[uf]}.")

    shutil.rmtree(caminho_temp, ignore_errors=True)

# Concatenando arquivos
caminho_concatenado = os.path.join(os.getcwd(), "Mosaico completo")
os.makedirs(caminho_concatenado, exist_ok=True)

concatenado_df = concatenar_arquivos(caminho_arquivos)

if concatenado_df is not None and not concatenado_df.empty:
    concatenado_df.to_csv(os.path.join(caminho_concatenado, "Mosaico_Brasil.csv"), index=False)
    print("Arquivo Mosaico_Brasil.csv criado com sucesso!")
else:
    print("Não foi possível criar o arquivo Mosaico_Brasil.csv, pois nenhum dado válido foi concatenado.")
