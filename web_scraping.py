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

        # criando uma instancia do Chrome e definindo nossas configurações (opcoes).
        navegador = webdriver.Chrome(options=opcoes)
        # Abrindo url no navegador
        navegador.get(url_anatel)
        # Esperando carregamento do próximo elemento.
        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "filtros_adicionais")))
        # Abrindo "filtros adicionais"
        navegador.find_element(By.ID, "filtros_adicionais").click()
        # Esperando carregamento do próximo elemento.
        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "fa_gsearch")))
        # Abrindo dropdown "Search by" e selecionando filtro por estado (UF)
        Select(navegador.find_element(By.ID, "fa_gsearch")).select_by_index(1)
        # Esperando carregamento do próximo elemento.
        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "fa_uf")))
        # Abrindo dropdown "fa_uf" e selecionando o estado (UF)
        Select(navegador.find_element(By.ID, "fa_uf")).select_by_value(f"{UFs[uf]}")
        # Esperando carregamento do próximo elemento.
        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "import")))
        # Clicando em enviar
        navegador.find_element(By.ID, "import").click()
        # Esperando a caixa de pesquisa desaparecer
        WebDriverWait(navegador, 60).until(EC.invisibility_of_element_located((By.ID, "wait_box")))
        # Esperando carregamento do próximo elemento.
        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "download_csv")))
        time.sleep(2)
        # Iniciando download
        navegador.find_element(By.ID, "download_csv").click()
        # Esperando a caixa de processamento desaparecer
        WebDriverWait(navegador, 60).until(EC.invisibility_of_element_located((By.ID, "wait_box")))
        # A partir desse ponto vamos presumir que o download tenha iniciado. Agora vamos monitorar a pasta destino para saber se o download foi um sucesso.

        # Iniciando monitoramento
        caminho_dowload = verifica_download(caminho_temp, tempo_limite, intervalo)
        # Retornando o resultado da verificação
        return caminho_dowload
    except Exception as error:
        # Definindo o que fazer em caso de erro
        print(error)
        shutil.rmtree(caminho_temp)
        return False
    finally:
        # Encerrando...
        navegador.quit()


# Função para verificar se o download foi concluído com sucesso
def verifica_download(caminho_temp, tempo_limite, intervalo):
    try:
        # Obtendo a hora de inicio da verificação
        tempo_inicio = time.time()
        # Iniciando a verificação
        while (time.time() - tempo_inicio) < tempo_limite:
            # Obtendo os arquivos .zip contidos na pasta
            arquivo_zip = [f for f in os.listdir(caminho_temp) if f.endswith('.zip')]
            # Verificando se o arquivo existe na pasta
            if arquivo_zip:
                print("Arquivo .zip encontrado:", arquivo_zip[0])
                caminho_completo = os.path.join(caminho_temp, arquivo_zip[0])
                return caminho_completo
            else:
                print("Arquivo .zip não encontrado, verificando novamente em 5 segundos...")
                time.sleep(intervalo)
        # Falha no download
        print("Tempo limite alcançado. Arquivo .zip não foi encontrado.")
        return False
    except Exception as error:
        # Definindo o que fazer em caso de erro
        print(error)


# Função para extrair o CSV do ZIP.
def extrai_csv(caminho_zip):
    # Abrindo ZIP
    with zipfile.ZipFile(caminho_zip, 'r') as zip:
        # Buscando por arquivos CSV
        arquivos_csv = [arquivo for arquivo in zip.namelist() if arquivo.endswith('.csv')]
        # Verificando o resultado da busca anterior
        if arquivos_csv:
            arquivo_csv = arquivos_csv[0]
            # Abrindo e lendo o CSV
            with zip.open(arquivo_csv) as csv:
                return pd.read_csv(csv, encoding='latin1', on_bad_lines='skip')
        else:
            print("Não econtrado arquivo cvs no zip.")


# Função para ETL do arquivo.
def processa_arquivo(arquivo):
    print(f"Iniciando processamento do arquivo {UFs[uf]}.csv")

    # Removendo espaços dos valores
    arquivo = arquivo.astype(str).map(str.strip)
    # Removendo espaços dos nomes das colunas
    arquivo.columns = arquivo.columns.str.strip()

    # Selecionando as colunas
    arquivo = arquivo[['NomeEntidade','NumFistel','NumServico','NumEstacao','SiglaUf','CodMunicipio','Tecnologia','FreqTxMHz','ClassInfraFisica','AlturaAntena','Latitude','Longitude',
                       'DataLicenciamento','DataPrimeiroLicenciamento','DataValidade','Municipio.NomeMunicipio']]

    # Renomeando as colunas
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

    # Convertendo os tipos corretamente
    # Substituindo [,;] por .
    arquivo['AlturaAntena'] = arquivo['AlturaAntena'].astype(str).str.replace('[,;]', '.', regex=True)
    # Dropando linhas com datas inválidas
    arquivo['DataPrimeiroLicenciamento'] = pd.to_datetime(arquivo['DataPrimeiroLicenciamento'], errors='coerce')
    arquivo.dropna(subset=['DataPrimeiroLicenciamento'], inplace=True)
    arquivo['DataUltimoLicenciamento'] = pd.to_datetime(arquivo['DataUltimoLicenciamento'], errors='coerce')
    arquivo.dropna(subset=['DataUltimoLicenciamento'], inplace=True)
    arquivo['NumEstacao'] = pd.to_datetime(arquivo['NumEstacao'], errors='coerce')
    arquivo.dropna(subset=['NumEstacao'], inplace=True)
    # Tipando as colunas
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
        'NomeMunicipio': 'str'
    })
    # Descartando colunas com frequencias ausentes
    arquivo['Frequencia'] = pd.to_numeric(arquivo['Frequencia'], errors='coerce')
    arquivo.dropna(subset=['Frequencia'], inplace=True)
    arquivo['AlturaAntena'] = pd.to_numeric(arquivo['AlturaAntena'], errors='coerce')
    arquivo.dropna(subset=['AlturaAntena'], inplace=True)
    
    # Filtrando os dados. Vamos utilizar apenas os dados de licenciamento movel
    arquivo = arquivo[arquivo['NumServico'] == 10]
    
    # Substituindo valores da coluna TipoInfra
    arquivo['TipoInfra'] = arquivo['TipoInfra'].replace('nan','Nao Especificado')

    # Renomeando valores da coluna Operadora
    arquivo['Operadora'] = arquivo['Operadora'].replace({
        'CLARO S.A.' : "CLARO",
        'TELEFONICA BRASIL S.A.' : "VIVO",
        'Telefonica Brasil S.a.':"VIVO",
        'TIM S A' : "TIM",
        'TIM S/A' : "TIM",
        'Brisanet Servicos de Telecomunicacoes S.A.': "BRISANET"
    })

    # Substituindo os valores de tecnologia de acordo com a geração correspondente
    arquivo['Tecnologia'] = arquivo['Tecnologia'].replace({
        'GSM': "2G",
        'WCDMA': "3G",
        'WDCMA': "3G",
        'LTE': "4G",
        'NR': "5G",
        '': "Nao Informado"
    })

    # Criando coluna com a data do download dos registros
    arquivo['DataDownload'] = datetime.now().strftime("%d/%m/%Y")

    return arquivo

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
        mensagem_erro = "Nenhum arquivo csv pôde ser lido com sucesso."
        # Retorna um DataFrame com a mensagem de erro
        return pd.DataFrame({'Erro': [mensagem_erro]})

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
# criando lista para iterar e que baixe o arquivo de todos os estados.
qtd_estados = list(range(1,28))

# Iniciando nossos downloads
for uf in qtd_estados:
    # Criando pasta temporária para receber o download
    caminho_temp = os.path.join(os.getcwd(), f"Mosaico - {UFs[uf]}")
    os.makedirs(caminho_temp, exist_ok=True)
    # Iniciando download 
    caminho_zip = download_arquivo(uf)
    
    # Verificando resultado do download
    if caminho_zip == False:
        print(f"Erro no download da UF {UFs[uf]}.")
        shutil.rmtree(caminho_temp)
    else:
        print("Sucesso no download!")
        csv = extrai_csv(caminho_zip)
        csv = processa_arquivo(csv)
        # Criando pasta para armazenar os arquivos
        caminho_arquivos = os.path.join(os.getcwd(), "arquivos Mosaico")
        os.makedirs(caminho_arquivos, exist_ok=True)
        csv.to_csv(os.path.join(f"{caminho_arquivos}\{UFs[uf]}.csv"), index=False)
        # Removendo pasta temp
        shutil.rmtree(caminho_temp)

# Criando pasta para armazenar um arquivo completo com todas as UFs.
caminho_concatenado = os.path.join(os.getcwd(), "Mosaico completo")
os.makedirs(caminho_concatenado, exist_ok=True)
# Concatenando os arquivos
concatenado = concatenar_arquivos(caminho_arquivos)
concatenado.to_csv(os.path.join(f"{caminho_concatenado}\Mosaico_Brasil.csv"), index=False)