from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()
#driver.implicitly_wait(10)
driver.get('https://consultas.anvisa.gov.br/#/bulario/')
driver.implicitly_wait(10)

# elements = writablle page section

# Numero de registro
element = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/form/div/div[2]/div[1]/div[2]/input")
element.send_keys("183260244")

element = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/form/div/div[3]/input[1]")
element.click()

element = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/form/div/div[2]/table/tbody/tr[2]/td[6]/a")
actions = ActionChains(driver)
actions.context_click(element).perform()
