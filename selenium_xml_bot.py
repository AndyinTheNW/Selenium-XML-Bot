from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from xml.etree import ElementTree
from xml.etree import ElementTree as ET
from datetime import datetime
import time
import os
import shutil
import zipfile
import numpy as np


def limpa_diretorios(*dirs):
    """
    Cleans the given directories by deleting all contents inside them, including files and folders.
    Does not delete the initial directory.

    Args:
        *dirs (str): List of directory paths to be cleaned.
    """
    for diretorio in dirs:
        if os.path.exists(diretorio):
            for file in os.listdir(diretorio):
                file_path = os.path.join(diretorio, file)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print("Failed to delete %s. Reason: %s" % (file_path, e))


def preparar_driver(diretorio_download, caminho_driver_chrome):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    prefs = {
        "download.default_directory": diretorio_download,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    webdriver_service = Service(
        r"D:\\Users\\erp93066\\python_login\\Executaveis\\robos_diarios\\chromedriver.exe"
    )
    driver = webdriver.Chrome(
        service=webdriver_service, options=chrome_options)
    return driver


def fazer_login(driver, url, nome_usuario, senha):
    driver.get(url)
    driver.find_element(By.NAME, "username").send_keys(nome_usuario)
    driver.find_element(By.NAME, "password").send_keys(senha)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    time.sleep(5)
    driver.find_element(By.ID, "closebutton").click()


def baixar_arquivos(driver, data_inicial, data_final):
    servidores = {
        "Servidor_empresa_RJ": "/html/body/div[1]/div[2]/div[1]/ul[1]/li[2]/div/div[2]/div[2]/div[4]/div",
        "Servidor_empresa_Brasil": "/html/body/div[1]/div[2]/div[1]/ul[1]/li[2]/div/div[2]/div[2]/div[2]/div",
    }

    for nome_servidor, xpath_servidor in servidores.items():
        print(f"Processando {nome_servidor}...")

        # Seleciona o servidor por xpath
        driver.find_element(
            By.XPATH, "/html/body/div[1]/div[2]/div[1]/ul[1]/li[2]/div"
        ).click()

        time.sleep(3)

        driver.find_element(By.XPATH, xpath_servidor).click()

        time.sleep(3)

        # Clicar em "Listagem NF-e" para acessar a página de listagem das NF-e
        driver.find_element(By.LINK_TEXT, "Listagem NF-e").click()

        # Selecionar o número 500 de registros exibidos por página (500)
        elemento_select = driver.find_element(By.CLASS_NAME, "ui-pg-selbox")
        select = Select(elemento_select)
        select.select_by_value("500")

        # Definir a Data Inicial da consulta
        driver.find_element(By.NAME, "consultaDataInicial").clear()
        driver.find_element(
            By.NAME, "consultaDataInicial").send_keys(data_inicial)
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.NAME, "consultaDataFinal"))
        ).clear()
        driver.find_element(By.NAME, "consultaDataFinal").send_keys(data_final)

        # Clicar no botão "Buscar"
        driver.find_element(By.ID, "listagem_atualiza").click()

        time.sleep(5)

        # Clicar no checkbox para selecionar todas as NF-e
        driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[2]/div[32]/div[3]/div[9]/div[3]/div[2]/div/table/thead/tr/th[12]/div/div/input",
        ).click()

        time.sleep(5)

        # Clicar no botão para baixar os arquivos XML em massa
        driver.find_element(By.XPATH, "//h3[text()='DOWNLOAD XML']").click()

        time.sleep(3)

        # Clicar no botão de download
        driver.find_element(By.ID, "downloadEmMassa").click()

        time.sleep(20)


def substituir_data_emissao(root, arquivo_xml, diretorio_extracao, tree):
    """
    Altera a data de emissão (dhEmi) no arquivo XML para o dia de download no formato "yyyy-mm-ddThh:mm:ss-03:00".
    """
    today = datetime.today()
    dhEmi = root.find(".//{http://www.portalfiscal.inf.br/nfe}dhEmi")
    if dhEmi is not None:
        dhEmi.text = today.strftime("%Y-%m-%dT%H:%M:%S-03:00")
        tree.write(os.path.join(diretorio_extracao, arquivo_xml))


def processar_arquivos(
    diretorio_download,
    diretorio_extracao,
    diretorio_empresa_RJ,
    diretorio_difal_RJ,
    diretorio_st_RJ,
    diretorio_empresa_Brasil,
    diretorio_difal_Brasil,
    diretorio_st_Brasil,
    diretorio_guias,
):
    os.makedirs(diretorio_download, exist_ok=True)
    os.makedirs(diretorio_guias, exist_ok=True)
    os.makedirs(diretorio_extracao, exist_ok=True)
    os.makedirs(diretorio_empresa_RJ, exist_ok=True)
    os.makedirs(diretorio_difal_RJ, exist_ok=True)
    os.makedirs(diretorio_st_RJ, exist_ok=True)
    os.makedirs(diretorio_empresa_Brasil, exist_ok=True)
    os.makedirs(diretorio_difal_Brasil, exist_ok=True)
    os.makedirs(diretorio_st_Brasil, exist_ok=True)

    arquivos = os.listdir(diretorio_download)
    arquivos_zip = [f for f in arquivos if f.endswith(".zip")]

    # REGRA: se o zip tiver (1) no final, extrai para o diretório "empresa_Brasil", caso contrário, extrai para o diretório "empresa_RJ"
    for arquivo_zip in arquivos_zip:
        with zipfile.ZipFile(
            os.path.join(diretorio_download, arquivo_zip), "r"
        ) as zip_ref:
            if arquivo_zip.endswith("(1).zip"):
                zip_ref.extractall(diretorio_empresa_Brasil)
            else:
                zip_ref.extractall(diretorio_empresa_RJ)

                print(f"arquivos extraidos com sucesso")

    Arquivos_Baixados_rj = os.listdir(diretorio_empresa_RJ)
    Arquivos_Baixados_brasil = os.listdir(diretorio_empresa_Brasil)
    Arquivos_Baixados_rj = [
        f for f in Arquivos_Baixados_rj if f.endswith(".xml")]
    Arquivos_Baixados_brasil = [
        f for f in Arquivos_Baixados_brasil if f.endswith(".xml")
    ]

    for arquivo_xml in Arquivos_Baixados_rj:
        tree = ElementTree.parse(os.path.join(
            diretorio_empresa_RJ, arquivo_xml))
        root = tree.getroot()
        substituir_data_emissao(root, arquivo_xml, diretorio_empresa_RJ, tree)
        mover_arquivos_com_base_no_valor(
            root, arquivo_xml, diretorio_empresa_RJ, diretorio_difal_RJ, diretorio_st_RJ
        )

    for arquivo_xml in Arquivos_Baixados_brasil:
        tree = ElementTree.parse(os.path.join(
            diretorio_empresa_Brasil, arquivo_xml))
        root = tree.getroot()
        substituir_data_emissao(
            root, arquivo_xml, diretorio_empresa_Brasil, tree)
        mover_arquivos_com_base_no_valor(
            root,
            arquivo_xml,
            diretorio_empresa_Brasil,
            diretorio_difal_Brasil,
            diretorio_st_Brasil,
        )


def mover_arquivos_com_base_no_valor(
    root, arquivo_xml, diretorio_extracao, diretorio_difal_RJ, diretorio_st_RJ
):
    IEST = root.find(".//{http://www.portalfiscal.inf.br/nfe}IEST")
    VICMSUFDEST = root.find(
        ".//{http://www.portalfiscal.inf.br/nfe}vICMSUFDest")
    VST = root.find(".//{http://www.portalfiscal.inf.br/nfe}vST")

    if IEST is not None:
        os.remove(os.path.join(diretorio_extracao, arquivo_xml))

    else:
        # Se vICMSUFDest existe, mover para o diretório de DIFAL
        if VICMSUFDEST is not None:
            shutil.move(
                os.path.join(diretorio_extracao, arquivo_xml),
                os.path.join(diretorio_difal_RJ, arquivo_xml),
            )
        else:
            # Se vST existe e seu valor é maior que 0, mover para o diretório de ST
            if VST is not None and float(VST.text) > 0:
                shutil.move(
                    os.path.join(diretorio_extracao, arquivo_xml),
                    os.path.join(diretorio_st_RJ, arquivo_xml),
                )
            else:
                # Caso nenhuma das condições seja atendida, descartar o arquivo
                os.remove(os.path.join(diretorio_extracao, arquivo_xml))


def extract_uf(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    ufdest_tag = root.find(
        ".//{http://www.portalfiscal.inf.br/nfe}dest/{http://www.portalfiscal.inf.br/nfe}enderDest/{http://www.portalfiscal.inf.br/nfe}UF"
    )
    if ufdest_tag is not None:
        return ufdest_tag.text
    return None


def rename_files_with_uf(directory):
    xml_files = [file for file in os.listdir(
        directory) if file.endswith(".xml")]

    for xml_file in xml_files:
        xml_path = os.path.join(directory, xml_file)
        uf = extract_uf(xml_path)

        if uf:
            new_name = f"{uf} - {xml_file}"
            new_path = os.path.join(directory, new_name)
            os.rename(xml_path, new_path)
            print(f"Renamed: {xml_file} -> {new_name}")


def deleta_arquivos_por_uf(diretorio_empresa_RJ, diretorio_empresa_Brasil):
    estados_para_descartar_empresa_RJ = ["RJ", "MG", "PR", "RS", "SC", "SP"]
    estados_para_descartar_empresa_Brasil = [
        "AM",
        "AP",
        "BA",
        "DF",
        "ES",
        "MA",
        "MG",
        "MS",
        "MT",
        "PE",
        "PR",
        "RJ",
        "RS",
        "SC",
        "SE",
        "SP",
    ]

    for uf in estados_para_descartar_empresa_RJ:
        for file in os.listdir(diretorio_empresa_RJ):
            if file.endswith(".xml"):
                if uf in file:
                    os.remove(os.path.join(diretorio_empresa_RJ, file))

    for uf in estados_para_descartar_empresa_Brasil:
        for file in os.listdir(diretorio_empresa_Brasil):
            if file.endswith(".xml"):
                if uf in file:
                    os.remove(os.path.join(diretorio_empresa_Brasil, file))


def principal(
    diretorio_download,
    caminho_driver_chrome,
    url,
    nome_usuario,
    senha,
    diretorio_extracao,
    diretorio_empresa_RJ,
    diretorio_difal_RJ,
    diretorio_st_RJ,
    diretorio_empresa_Brasil,
    diretorio_st_Brasil,
    diretorio_difal_Brasil,
    data_inicial,
    data_final,
    diretorio_guias,
):
    limpa_diretorios(diretorio_download, diretorio_extracao, diretorio_guias)
    driver = preparar_driver(diretorio_download, caminho_driver_chrome)
    fazer_login(driver, url, nome_usuario, senha)
    baixar_arquivos(driver, data_inicial, data_final)
    processar_arquivos(
        diretorio_download,
        diretorio_extracao,
        diretorio_empresa_RJ,
        diretorio_difal_RJ,
        diretorio_st_RJ,
        diretorio_empresa_Brasil,
        diretorio_difal_Brasil,
        diretorio_st_Brasil,
        diretorio_guias,
    )


dt_fim_texto = open(
    "d:\\Users\\erp93066\\python_login\\Executaveis\\dia_fim.txt", "r")
dt_fim = dt_fim_texto.read()
print(dt_fim)

dt_inicio_texto = open(
    "d:\\Users\\erp93066\\python_login\\Executaveis\\dia_inic.txt", "r"
)
dt_inicio = dt_inicio_texto.read()
print(dt_inicio)

if __name__ == "__main__":
    limpa_diretorios(
        "D:/Users/erp93066/python_login/downloads",
        "D:/Users/erp93066/python_login/Arquivos_Baixados",
        "D:/Users/erp93066/python_login/guias",
    )
    principal(
        diretorio_download=r"D:\Users\erp93066\python_login\downloads",
        caminho_driver_chrome="D:/Users/erp93066/python_login/chromedriver-win64",
        url="http://136.239.170.38:8080/portal/mvc/login",
        nome_usuario="robodw",
        senha="dwrobo",
        diretorio_extracao="D:/Users/erp93066/python_login/Arquivos_Baixados",
        diretorio_empresa_Brasil="D:/Users/erp93066/python_login/Arquivos_Baixados/empresa_Brasil",
        diretorio_difal_Brasil="D:/Users/erp93066/python_login/Arquivos_Baixados/empresa_Brasil/difal_Brasil",
        diretorio_st_Brasil="D:/Users/erp93066/python_login/Arquivos_Baixados/empresa_Brasil/st_Brasil",
        diretorio_empresa_RJ="D:/Users/erp93066/python_login/Arquivos_Baixados/empresa_RJ",
        diretorio_difal_RJ="D:/Users/erp93066/python_login/Arquivos_Baixados/empresa_RJ/difal_RJ",
        diretorio_st_RJ="D:/Users/erp93066/python_login/Arquivos_Baixados/empresa_RJ/st_RJ",
        diretorio_guias="D:/Users/erp93066/python_login/guias",
        data_inicial=str(dt_inicio),
        data_final=str(dt_fim),
    )


rename = [
    r"D:\Users\erp93066\python_login\Arquivos_Baixados\empresa_Brasil\st_Brasil",
    r"D:\Users\erp93066\python_login\Arquivos_Baixados\empresa_Brasil\difal_Brasil",
    r"D:\Users\erp93066\python_login\Arquivos_Baixados\empresa_RJ\st_RJ",
    r"D:\Users\erp93066\python_login\Arquivos_Baixados\empresa_RJ\difal_RJ",
]

for directory in rename:
    if os.path.exists(directory):
        print(f"Processing directory: {directory}")
        rename_files_with_uf(directory)
    else:
        print(f"Directory not found: {directory}")
os.system(
    r"d:\\Users\\erp93066\\python_login\\Executaveis\\robos_diarios\\DIFAL_RJ.py")
