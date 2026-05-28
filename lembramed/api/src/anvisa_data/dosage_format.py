import os,json,time,glob,logging,pprint
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib3.exceptions import ReadTimeoutError
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException,
    ElementClickInterceptedException,
)
from selenium.webdriver.support import expected_conditions as EC
from web_navigator import (
    _build_options, initialize_driver, quit_driver, _wait_overlay_gone,
    load_checkpoint, save_checkpoint, _driver_is_alive, _restart_driver
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

URL = "https://consultas.anvisa.gov.br/#/medicamentos/?numeroProcesso="
CHECKPOINT_FILE = "checkpoint.json"
RESTART_EVERY     = 30
MAX_CONSECUTIVE_FAILURES = 3
PAGE_LOAD_WAIT    = 15

OK           = 0
NOT_FOUND    = 1
DRIVER_ERROR = 2

def wait_for_overlay(driver:webdriver.Firefox):
    """ Wait for loading overlay of the angular disapear """
    try:
        WebDriverWait(driver,PAGE_LOAD_WAIT).until(
        EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, "div.dw-loading-overlay.dw-loading-active")
        ))
    except TimeoutException:
        pass

# BUSCA AVANCADA
# /html/body/div[3]/div[1]/form/div/div[2]/div[4]

# NUMERO PROCESSO
# /html/body/div[3]/div[1]/form/div/div[2]/div[4]/div[3]

# CONSULTAR
# /html/body/div[3]/div[1]/form/div/div[3]/input[1]

def open_dosage_format(process_num:str, driver:webdriver.Firefox):
    """Open the screen of the medications table that references this process_num on browser"""

    try:
        driver.get(URL + process_num)
        wait = WebDriverWait(driver,PAGE_LOAD_WAIT)

        consult_button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[3]/div[1]/form/div/div[3]/input[1]")
            )
        )
        consult_button.click()

        wait_for_overlay(driver)
        
        table_button = wait.until(
            EC.presence_of_element_located(
                (By.ID, "containerTable")
            )
        )
        wait_for_overlay(driver)

        output_dict = get_register(driver)

        table_button.click()

        wait_for_overlay(driver)
        
        medication_button = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[ng-if=\"produto.tipoAutorizacao === 'REGISTRADO'\"]"))
        )

        return OK, output_dict

    except (TimeoutException, NoSuchElementException):
        log.info(f"Sem informacoes sobre: {process_num}.")
        return NOT_FOUND, None

    except (WebDriverException, ReadTimeoutError) as e:
        msg = e.msg.splitlines()[0] if hasattr(e, 'msg') else str(e).splitlines()[0]
        log.error(f"Erro no driver para: {process_num}]\n{msg}")
        return DRIVER_ERROR, None

def get_register(driver:webdriver.Firefox):
    """Filters the data for Register instance with: regulation_num(int) and and expiration_date(date)"""

    output_dict = {}
    container_initial_table = driver.find_element(By.ID, "containerTable")
    initial_table = container_initial_table.find_element(By.TAG_NAME, "table")
    rows = initial_table.find_elements(By.CSS_SELECTOR, 'tr[ng-repeat="produto in produtos"]')

    for row in rows:
        tds = row.find_elements(By.TAG_NAME,"td")

        if (tds[3].text.strip() == "REGISTRADO" and tds[8].find_elements(By.TAG_NAME, "span")):
            output_dict["expiration_date"] = tds[10].text.strip()
            output_dict["regulation_num"] = tds[5].text.strip()

    return output_dict

def get_dosage_formato(driver:webdriver.Firefox):
    """returns dict with: dosage(list), formato(string)"""

    output_dict = {}

    # OUTPUT EXPECTED SHAPE:
    #
    # output_dict = {
    #     "register_num_ex1":
    #     {
    #         "dosage" : "100ml",
    #         "formato" : "XAROPE",
    #     }
    #     "register_num_ex2":
    #     {
    #         ...
    #     }
    # }

    container = driver.find_element(By.CSS_SELECTOR, "div[ng-if=\"produto.tipoAutorizacao === 'REGISTRADO'\"]")
    table = container.find_element(By.TAG_NAME, "table")
    tbodies = table.find_elements(By.CSS_SELECTOR, 'tbody[class="ng-scope"]')

    # STRUCTURE INSIDE A TBODY:
    #
    # ONE - <tr ng-click="expandirDetalhe(apresentacao)" style="cursor:pointer">
    # with: ... dosage(1), register(2), formato(3) ...
    #
    # ONZE - <tr ng-show="apresentacao.exibirDetalhe" class="ng-hide">
    # with: embalagem(2), administration(4), conservation(5), prescription_restriction(6)
    # ... usage_restriction(7), label(9), can_be_fractioned(10)

    for tbody in tbodies:
        main_row = tbody.find_element(By.CSS_SELECTOR, 'tr[ng-click="expandirDetalhe(apresentacao)"]')
        main_tds = main_row.find_elements(By.TAG_NAME, "td")

        # if main_tds[1].find_element(By.TAG_NAME, "span").text != "Ativo":
        #     continue

        spans = main_tds[1].find_elements(By.TAG_NAME, "span")
        if not spans or spans[0].text.strip() != "Ativo":
            continue

        trs = tbody.find_elements(By.CSS_SELECTOR, 'tr[ng-show="apresentacao.exibirDetalhe"]')
        sub = {}

        try:
            # RAW DOSAGE DATA SHAPE :
            #
            # [CONCENTRAÇÃO] [FORMA FARMACÊUTICA] [EMBALAGEM] X [QUANTIDADE]
            # 100 UI/ML       SOL INJ              CT FA        X  10 ML
            # 5 MG            COM                 CT BL AL...   X  7
            #
            sub["dosage"] = main_tds[1].text.strip()
        except NoSuchElementException:
            sub["dosage"] = ""
        
        try:
            registro = main_tds[2].text.strip()
        except NoSuchElementException:
            registro = ""

        try:
            bloco = trs[0].find_element(By.TAG_NAME, "td")
            active_ingredients = bloco.find_elements(By.CSS_SELECTOR, 'div[ng-repeat="pa in apresentacao.principiosAtivos track by $index"]')
            order = [ai.get_attribute("textContent").strip() for ai in active_ingredients]
            sub["concentration_order"] = order
        except NoSuchElementException:
            sub["concentration_order"] = ""

        try:
            embalagens = {}
            list_container = trs[2].find_element(By.TAG_NAME, "td")
            unordered_list = list_container.find_element(By.TAG_NAME, "ul")
            lists = list_container.find_elements(By.TAG_NAME, "li")
            for l in lists:
                classification = l.find_element(By.TAG_NAME, "span").get_attribute("textContent").strip()
                value = l.get_attribute("textContent").strip().split(" - ")[-1]
                embalagens[f"{classification}"] = value
            sub["embalagem"] = embalagens
        except NoSuchElementException:
            sub["embalagem"] = {}

        try:
            # div ng-repeat="va in apresentacao.viasAdministracao"
            block = trs[4].find_element(By.TAG_NAME, "td")
            sub["administration"] = block.find_element(By.CSS_SELECTOR, 'div[ng-repeat="va in apresentacao.viasAdministracao"]').get_attribute("textContent").strip()
        except NoSuchElementException:
            sub["administration"] = ""

        try:
            # div ng-repeat="c in apresentacao.conservacao"
            blockk = trs[5].find_element(By.TAG_NAME, "td")
            sub["conservation"] = blockk.find_element(By.CSS_SELECTOR, 'div[ng-repeat="c in apresentacao.conservacao"]').get_attribute("textContent").strip()
        except NoSuchElementException:
            sub["conservation"] = ""

        try:
            # div ng-repeat="rp in apresentacao.restricaoPrescricao"
            blockkk = trs[6].find_element(By.TAG_NAME, "td")
            sub["prescription_restriction"] = blockkk.find_element(By.CSS_SELECTOR, 'div[ng-repeat="rp in apresentacao.restricaoPrescricao"]').get_attribute("textContent").strip()
        except NoSuchElementException:
            sub["prescription_restriction"] = ""

        try:
            # div ng-repeat="ru in apresentacao.restricaoUso"
            blo = trs[7].find_element(By.TAG_NAME, "td")
            sub["usage_restriction"] = blo.find_element(By.CSS_SELECTOR, 'div[ng-repeat="ru in apresentacao.restricaoUso"]').get_attribute("textContent").strip()
        except NoSuchElementException:
            sub["usage_restriction"] = ""
        
        try:
            # div ng-if="apresentacao.tarja"
            bl = trs[9].find_element(By.TAG_NAME, "td")
            sub["label"] = bl.find_element(By.CSS_SELECTOR, 'div[ng-if="apresentacao.tarja"]').get_attribute("textContent").strip()
        except NoSuchElementException:
            sub["label"] = ""

        try:
            # div ng-if="apresentacao.apresentacaoFracionada"
            b = trs[10].find_element(By.TAG_NAME, "td")
            if b.find_element(By.CSS_SELECTOR, 'div[ng-if="apresentacao.apresentacaoFracionada"]').get_attribute("textContent").strip().upper() == "SIM":
                sub["can_be_fractioned"] = True
            else:
                sub["can_be_fractioned"] = False
        except NoSuchElementException:
            sub["can_be_fractioned"] = False

        output_dict.update({str(registro): sub})
    
    return output_dict

def run_scraper(process_nums: list[str], file_num:int,restart_every: int = RESTART_EVERY):
    """Main logic of the medication scraping"""

    done = load_checkpoint()
    remaining = [pn for pn in process_nums if pn not in done]
    log.info(f"Total: {len(process_nums)} | Já feitos: {len(done)} | Restantes: {len(remaining)}")

    FIRST_ITERATION = True

    success_count = 0
    consecutive_errors = 0
    dumped_json_instances = 0

    try:
        for pn in remaining:
            local_dict = {}

            if (FIRST_ITERATION):
                driver = initialize_driver(URL + str(pn))
                FIRST_ITERATION = False

            if success_count > 0 and success_count % restart_every == 0:
                log.info(f"Reinicio preventivo apos {success_count} downloads.")
                driver = _restart_driver(driver, URL + str(pn))

            status,register_data = open_dosage_format(str(pn), driver)
            if register_data != None:
                local_dict.update(register_data)

            presentation_dict = {}

            if status == OK:
                consecutive_errors = 0
                done.add(str(pn))
                save_checkpoint(done)
                success_count += 1
                presentation_dict["presentations"] = get_dosage_formato(driver)
                local_dict.update(presentation_dict)

            elif status == NOT_FOUND:
                consecutive_errors = 0
                log.info(f"[{pn}] Sem medicacao — marcado no checkpoint.")
                done.add(str(pn))
                save_checkpoint(done)

            elif status == DRIVER_ERROR:
                consecutive_errors += 1
                log.warning(
                    f"[{pn}] Erro de driver ({consecutive_errors}/{MAX_CONSECUTIVE_FAILURES}). "
                    f"NÃO marcado no checkpoint."
                )
                driver = _restart_driver(driver, URL + str(pn))

                if consecutive_errors >= MAX_CONSECUTIVE_FAILURES:
                    log.error(
                        f"[{pn}] {MAX_CONSECUTIVE_FAILURES} erros seguidos mesmo após reinícios. "
                        f"Pulando este número para não travar o script."
                    )
                    done.add(str(pn))
                    save_checkpoint(done)
                    consecutive_errors = 0

            file_path = Path(f"dosage_formato{file_num}.json")

            if not file_path.exists():
                with open(f"dosage_formato{file_num}.json", "w") as f:
                    f.write("{}")
    
            with open(f"dosage_formato{file_num}.json", "r+") as f:
                cur = json.load(f)
                cur.update({str(pn): local_dict})
                f.seek(0)
                json.dump(cur, f, indent=4, ensure_ascii=False)
                dumped_json_instances += 1

    except KeyboardInterrupt:
        log.info("Interrompido pelo user, progresso salvo em checkpoint.json.")
    finally:
        print(f"Process finished, {dumped_json_instances} medications parsed written to 'dosage_formato.json'")
        quit_driver(driver)