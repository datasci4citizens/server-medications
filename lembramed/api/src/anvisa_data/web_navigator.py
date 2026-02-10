from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

def get_bula(registerNum):
    """A partir de um numero de registro (e empresa, opcional) abre o pdf respectivo
    a bula do paciente daquele medicamento (banco de dados da ANVISA)"""

    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    options.set_preference("pdfjs.disabled", False)  
    options.set_preference("pdfjs.firstRun", True)

    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get('https://consultas.anvisa.gov.br/#/bulario/')
    driver.implicitly_wait(10)

    # elements = writablle page section

    # Numero de registro
    element = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/form/div/div[2]/div[1]/div[2]/input")
    element.send_keys(registerNum)

    element = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/form/div/div[3]/input[1]")
    element.click()

    # element = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/form/div/div[2]/table/tbody/tr[2]/td[6]/a")
    # actions = ActionChains(driver)
    # actions.context_click(element).perform()

    botao_bula_paciente = driver.find_element(By.XPATH, "//a[@ng-if='produto.idBulaPacienteProtegido']")
    botao_bula_paciente.click()

# get_bula('183260244')