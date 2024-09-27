import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# Função para download do arquivo
def download_arquivo():
    try:
        # Definindo a url a ser acessada
        url_anatel = "https://sistemas.anatel.gov.br/se/public/view/b/licenciamento.php"
        
        # Criando pasta temporária para receber os downloads
        caminho_temp = os.path.join(os.getcwd(), "mosaico")
        os.makedirs(caminho_temp, exist_ok=True)

        # criando uma isntancia do chrome_options
        opcoes = webdriver.ChromeOptions()
        #opcoes.add_argument("--headless") # Argumento para baixar em segundo plano
        opcoes.add_experimental_option("prefs", {
            "download.deafult_directory": caminho_temp,
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
        Select(navegador.find_element(By.ID, "fa_uf")).select_by_value("ES")
        # Esperando carregamento do próximo elemento.
        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "import")))
        # Clicando em enviar
        navegador.find_element(By.ID, "import").click()
        # Esperando a caixa de pesquisa desaparecer
        WebDriverWait(navegador, 60).until(EC.invisibility_of_element_located(By.ID, "wait_box"))
        




        time.sleep(15)

        # Encerrando...
        navegador.quit()
        shutil.rmtree(caminho_temp)
    # Definindo o que fazer em caso de erro
    except Exception as error:
        print(error)
        navegador.quit()
        shutil.rmtree(caminho_temp)


# Iniciando nosso download
download_arquivo()