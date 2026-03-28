import os
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC

def get_last_downloaded_file(download_dir):
        files = os.listdir(download_dir)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(download_dir, x)))
        return files[-1] if files else None

def initialize_driver(path_dowload):
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", path_dowload)
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    options.set_preference("pdfjs.disabled", False)  
    options.set_preference("pdfjs.firstRun", True)
    # set_preference("--headless")
    driver = webdriver.Firefox(options=options)
    return driver

def download_bula(registerNum, driver):
    """A partir de um numero de registro (e empresa, opcional) baixa o pdf respectivo
    a bula do paciente daquele medicamento (banco de dados da ANVISA)"""

    path_dowload = "/home/yanetti/Desktop/extensao/server-medications/lembramed/api/src/anvisa_data/data"

    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", path_dowload)
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    options.set_preference("pdfjs.disabled", False)  
    options.set_preference("pdfjs.firstRun", True)
    driver = webdriver.Firefox(options=options)

    # driver = driver
    driver.get('https://consultas.anvisa.gov.br/#/bulario/')

    # Numero de registro
    wait = WebDriverWait(driver, 15)
    element = wait.until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[1]/form/div/div[2]/div[1]/div[2]/input"))
    )
    element.send_keys(registerNum)

    try:
        wait = WebDriverWait(driver, 5)
        element = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[1]/form/div/div[3]/input[1]"))
        )
        element.click()
    except (NoSuchElementException):
        driver.quit()
        return 1
    
    # Problema se nao achar registro com o register number em questao

    # element = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/form/div/div[2]/table/tbody/tr[2]/td[6]/a")
    # actions = ActionChains(driver)
    # actions.context_click(element).perform()

    try:
        wait = WebDriverWait(driver, 5)
        botao_bula_paciente = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@ng-if='produto.idBulaPacienteProtegido']"))
        )
        botao_bula_paciente.click()
    except TimeoutException:
        driver.quit()
        return 1
    
    # Esperar ate baixar e depois fechar o navegador
    try:
        wait = WebDriverWait(driver, 15)
        wait.until(EC.number_of_windows_to_be(2))
        # wait.until(get_last_downloaded_file("data/") != None)
        # WebDriverWait(driver, 120, 1).until(get_last_downloaded_file)
    except TimeoutException:
        driver.quit()
        return 1

    driver.quit()
    return 0

# download_bula('183260244')
# f_name = get_last_downloaded_file('data/')
# print(f_name)