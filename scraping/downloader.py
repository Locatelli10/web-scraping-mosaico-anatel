import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def configurar_navegador(caminho_download: str):
    opcoes = webdriver.ChromeOptions()
    # opcoes.add_argument("--headless")
    opcoes.add_experimental_option("prefs", {
        "download.default_directory": caminho_download,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    return webdriver.Chrome(options=opcoes)

def download_arquivo(uf, caminho_temp, tempo_limite, intervalo, ufs):
    navegador = None
    try:
        navegador = configurar_navegador(caminho_temp)
        navegador.get("https://sistemas.anatel.gov.br/se/public/view/b/licenciamento.php")

        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "filtros_adicionais"))).click()
        Select(navegador.find_element(By.ID, "fa_gsearch")).select_by_index(1)
        Select(navegador.find_element(By.ID, "fa_uf")).select_by_value(f"{ufs[uf]}")

        navegador.find_element(By.ID, "import").click()
        WebDriverWait(navegador, 60).until(EC.invisibility_of_element_located((By.ID, "wait_box")))
        WebDriverWait(navegador, 60).until(EC.presence_of_element_located((By.ID, "download_csv")))

        time.sleep(2)
        navegador.find_element(By.ID, "download_csv").click()
        WebDriverWait(navegador, 60).until(EC.invisibility_of_element_located((By.ID, "wait_box")))

        return verifica_download(caminho_temp, tempo_limite, intervalo)

    except Exception as e:
        print("Erro no download:", e)
        shutil.rmtree(caminho_temp)
        return None
    finally:
        if navegador:
            navegador.quit()

def verifica_download(caminho_temp, tempo_limite, intervalo):
    tempo_inicio = time.time()
    while (time.time() - tempo_inicio) < tempo_limite:
        arquivos = [f for f in os.listdir(caminho_temp) if f.endswith('.zip')]
        if arquivos:
            return os.path.join(caminho_temp, arquivos[0])
        print("Aguardando download...")
        time.sleep(intervalo)
    print("Download não encontrado no tempo limite.")
    return None
