import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Função para verificar se o download foi concluído com sucesso
def verifica_download(caminho_temp, tempo_limite, intervalo):
    try:
        tempo_inicio = time.time()
        while (time.time() - tempo_inicio) < tempo_limite:
            arquivos_zip = [f for f in os.listdir(caminho_temp) if f.endswith('.zip')]
            if arquivos_zip:
                print("Arquivo .zip encontrado:", arquivos_zip[0])
                return os.path.join(caminho_temp, arquivos_zip[0])
            print(f"Arquivo .zip não encontrado, tentando novamente em {intervalo} segundos...")
            time.sleep(intervalo)
        print("Tempo limite alcançado. Arquivo .zip não foi encontrado.")
        return False
    except Exception as error:
        print("Erro na verificação de download:", error)
        return False

# Função para download do arquivo
def download_arquivo(uf, caminho_temp, UFs, tempo_limite, intervalo):
    navegador = None
    try:
        url = "https://sistemas.anatel.gov.br/se/public/view/b/licenciamento.php"
        opcoes = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": caminho_temp,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        opcoes.add_experimental_option("prefs", prefs)
        navegador = webdriver.Chrome(options=opcoes)
        navegador.get(url)

        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "filtros_adicionais"))).click()
        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "fa_gsearch")))
        Select(navegador.find_element(By.ID, "fa_gsearch")).select_by_index(1)
        Select(navegador.find_element(By.ID, "fa_uf")).select_by_value(f"{UFs[uf]}")
        navegador.find_element(By.ID, "import").click()
        WebDriverWait(navegador, 60).until(EC.invisibility_of_element_located((By.ID, "wait_box")))

        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "download_csv")))
        time.sleep(2)
        navegador.find_element(By.ID, "download_csv").click()
        WebDriverWait(navegador, 60).until(EC.invisibility_of_element_located((By.ID, "wait_box")))

        return verifica_download(caminho_temp, tempo_limite, intervalo)

    except Exception as error:
        print("Erro no download:", error)
        shutil.rmtree(caminho_temp, ignore_errors=True)
        return False
    finally:
        if navegador:
            navegador.quit()
