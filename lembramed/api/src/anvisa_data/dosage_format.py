import os,json,time,glob,logging
from selenium import webdriver
from selenium.webdriver.common.by import By
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

URL = "https://consultas.anvisa.gov.br/#/medicamentos/?numeroProcesso=250000327219903"
CHECKPOINT_FILE = "checkpoint.json"
RESTART_EVERY     = 40   
MAX_CONSECUTIVE_FAILURES = 3 
PAGE_LOAD_WAIT    = 15
DOWNLOAD_WAIT     = 30

OK           = 0   # bula baixada com sucesso
NOT_FOUND    = 1   # registro existe mas não tem bula do paciente — salvar no checkpoint
DRIVER_ERROR = 2   # driver travou / sessão morta — NÃO salvar no checkpoint, reiniciar

# BUSCA AVANCADA
# /html/body/div[3]/div[1]/form/div/div[2]/div[4]

# NUMERO PROCESSO
# /html/body/div[3]/div[1]/form/div/div[2]/div[4]/div[3]

# CONSULTAR
# /html/body/div[3]/div[1]/form/div/div[3]/input[1]

def get_dosage_format(process_num:str ,driver:webdriver.Firefox):
    try:
        driver.get(URL)

        wait = WebDriverWait(driver,PAGE_LOAD_WAIT)
        # botao_busca_avancada = wait.until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, "/html/body/div[3]/div[1]/form/div/div[2]/div[4]/input")
        #     ) # /html/body/div[3]/div[1]/form/div/div[2]/div[4] XPATH FULL
        # )
        # botao_busca_avancada.click()

        # campo_numero_processo = wait.until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, "/html/body/div[3]/div[1]/form/div/div[2]/div[4]/div[3]")
        #     )
        # )
        # campo_numero_processo.clear()
        # campo_numero_processo.send_keys(process_num)

        # _wait_overlay_gone(driver)

        # wait_short = WebDriverWait(driver,8)
        botao_consultar = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[3]/div[1]/form/div/div[3]/input[1]")
            )
        )
        botao_consultar.click()

    except (TimeoutException, NoSuchElementException):
        log.info(f"[{process_num}] Sem bula do paciente.")
        return NOT_FOUND, None

    except WebDriverException as e:
        log.error(f"[{process_num}] WebDriverException: {e.msg.splitlines()[0]}")
        return DRIVER_ERROR, None

def run_scraper(
    process_nums: list[str],
    output_dict: dict,
    restart_every: int = RESTART_EVERY,
) -> dict:
    """
    NOT_FOUND: marca no checkpoint, não tenta de novo
    DRIVER_ERROR: NÃO marca no checkpoint, reinicia driver, tenta de novo
    """
    done = load_checkpoint()
    remaining = [n for n in process_nums if n not in done]
    log.info(f"Total: {len(process_nums)} | Já feitos: {len(done)} | Restantes: {len(remaining)}")

    # process_nums[0] to endpoint => just click "consultar"
    driver = initialize_driver(URL)
    success_count      = 0
    consecutive_errors = 0

    # URL + PROCESSNUM
    get_dosage_format(250000327219903, driver)

    # try:
    #     i = 0
    #     while i < len(remaining):
    #         num = remaining[i]
    #         if success_count > 0 and success_count % restart_every == 0:
    #             log.info(f"Reinício preventivo após {success_count} downloads.")
    #             driver = _restart_driver(driver, download_dir)

    #         log.info(f"[{i+1}/{len(remaining)}] {num}…")
    #         status, filename = download_bula(num, driver, download_dir)

    #         if status == OK:
    #             consecutive_errors = 0
    #             filepath = os.path.join(download_dir, filename)
    #             try:
    #                 data = process_fn(filepath)
    #                 if data:
    #                     output_dict[num] = data
    #             except Exception as e:
    #                 log.error(f"[{num}] Erro ao processar PDF: {e}")
    #             finally:
    #                 if os.path.exists(filepath):
    #                     os.remove(filepath)
    #             done.add(num)
    #             save_checkpoint(done)
    #             success_count += 1
    #             i += 1
    #         elif status == NOT_FOUND:
    #             consecutive_errors = 0
    #             log.info(f"[{num}] Sem bula — marcado no checkpoint.")
    #             done.add(num)
    #             save_checkpoint(done)
    #             i += 1

    #         elif status == DRIVER_ERROR:
    #             consecutive_errors += 1
    #             log.warning(
    #                 f"[{num}] Erro de driver ({consecutive_errors}/{MAX_CONSECUTIVE_FAILURES}). "
    #                 f"NÃO marcado no checkpoint."
    #             )
    #             driver = _restart_driver(driver, download_dir)

    #             if consecutive_errors >= MAX_CONSECUTIVE_FAILURES:
    #                 log.error(
    #                     f"[{num}] {MAX_CONSECUTIVE_FAILURES} erros seguidos mesmo após reinícios. "
    #                     f"Pulando este número para não travar o script."
    #                 )
    #                 done.add(num)
    #                 save_checkpoint(done)
    #                 consecutive_errors = 0
    #                 i += 1

    # except KeyboardInterrupt:
    #     log.info("Interrompido pelo usuário. Progresso salvo.")
    # finally:
    #     quit_driver(driver)

    # return output_dict