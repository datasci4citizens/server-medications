import os
import time
import json
import glob
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException,
    ElementClickInterceptedException,
)

from selenium.webdriver.support import expected_conditions as EC

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
ANVISA_URL        = "https://consultas.anvisa.gov.br/#/bulario/"
RESTART_EVERY     = 40   # reinicia o driver a cada N downloads bem-sucedidos
MAX_CONSECUTIVE_FAILURES = 3   # reinicia imediatamente após N falhas seguidas de driver
PAGE_LOAD_WAIT    = 15
DOWNLOAD_WAIT     = 30
CHECKPOINT_FILE   = "checkpoint.json"

# Códigos de retorno de download_bula
OK           = 0   # bula baixada com sucesso
NOT_FOUND    = 1   # registro existe mas não tem bula do paciente — salvar no checkpoint
DRIVER_ERROR = 2   # driver travou / sessão morta — NÃO salvar no checkpoint, reiniciar


# ── Driver helpers ────────────────────────────────────────────────────────────

def _build_options(download_dir: str) -> Options:
    """Build Firefox options – centralised so restart reuses the same config."""
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    options.set_preference("pdfjs.disabled", True)   # let Firefox save instead of open
    options.set_preference("pdfjs.firstRun", True)
    # Uncomment the next line to run headless (no visible window):
    # options.add_argument("--headless")
    return options


def initialize_driver(download_dir: str) -> webdriver.Firefox:
    """Create and return a fresh Firefox driver."""
    driver = webdriver.Firefox(options=_build_options(download_dir))
    log.info("Driver initialised.")
    return driver


def quit_driver(driver: webdriver.Firefox) -> None:
    """Safely quit the driver, ignoring already-dead sessions."""
    try:
        driver.quit()
    except Exception:
        pass


# ── Download helpers ──────────────────────────────────────────────────────────

def get_last_downloaded_file(download_dir: str) -> str | None:
    """Return the most-recently modified file in download_dir, or None."""
    files = [
        f for f in glob.glob(os.path.join(download_dir, "*"))
        if not f.endswith(".part")          # ignore incomplete Firefox downloads
    ]
    if not files:
        return None
    files.sort(key=os.path.getmtime)
    return os.path.basename(files[-1])


def _wait_for_new_pdf(download_dir: str, files_before: set, timeout: int = DOWNLOAD_WAIT) -> str | None:
    """
    Poll the download directory until a new file (not in files_before) appears
    and is fully written (no .part sibling).  Returns the filename or None.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        current = set(
            f for f in os.listdir(download_dir)
            if not f.endswith(".part")
        )
        new_files = current - files_before
        if new_files:
            return new_files.pop()
        time.sleep(1)
    return None


# ── Checkpoint helpers ────────────────────────────────────────────────────────

def load_checkpoint() -> set:
    """Return the set of register numbers already processed."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            return set(json.load(f))
    return set()


def save_checkpoint(done: set) -> None:
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(list(done), f)


# ── Core scraping function ────────────────────────────────────────────────────

OVERLAY_XPATH = "//div[contains(@class,'dw-loading-active')]"

def _wait_overlay_gone(driver, timeout=15):
    """Aguarda o overlay de loading da ANVISA desaparecer antes de interagir."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.XPATH, OVERLAY_XPATH))
        )
    except TimeoutException:
        pass  # se não sumir em 15s, tenta mesmo assim


def _driver_is_alive(driver: webdriver.Firefox) -> bool:
    """Testa se a sessão do driver ainda responde."""
    try:
        _ = driver.current_url
        return True
    except Exception:
        return False


def download_bula(register_num: str, driver: webdriver.Firefox, download_dir: str) -> tuple[int, str | None]:
    """
    Baixa a bula do paciente para *register_num*.

    Retorna:
        (OK,           filename)  – sucesso
        (NOT_FOUND,    None)      – sem bula no registro — marcar checkpoint
        (DRIVER_ERROR, None)      – driver morto / sessão travada — NÃO marcar checkpoint, reiniciar
    """
    # Checa sessão antes de tentar — evita timeout de 15s desnecessário
    if not _driver_is_alive(driver):
        log.error(f"[{register_num}] Driver morto antes de começar.")
        return DRIVER_ERROR, None

    files_before = set(
        f for f in os.listdir(download_dir)
        if not f.endswith(".part")
    )

    try:
        driver.get(ANVISA_URL)

        # ── Preenche número de registro ──────────────────────────────────────
        wait = WebDriverWait(driver, PAGE_LOAD_WAIT)
        campo_registro = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[3]/div[1]/form/div/div[2]/div[1]/div[2]/input")
            )
        )
        campo_registro.clear()
        campo_registro.send_keys(register_num)

        # ── Clica em pesquisar via JS — ignora overlay ───────────────────────
        botao_pesquisar = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[3]/div[1]/form/div/div[3]/input[1]")
            )
        )
        driver.execute_script("arguments[0].click();", botao_pesquisar)

        # ── Aguarda overlay sumir APÓS pesquisar antes de procurar o botão de bula
        _wait_overlay_gone(driver)

        # ── Clica na bula do paciente via JS ────────────────────────────────
        # Timeout curto aqui é correto: se o botão não aparecer em 8s, é NOT_FOUND
        wait_short = WebDriverWait(driver, 8)
        botao_bula_paciente = wait_short.until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[@ng-if='produto.idBulaPacienteProtegido']")
            )
        )
        driver.execute_script("arguments[0].click();", botao_bula_paciente)

        # ── Aguarda PDF no disco ─────────────────────────────────────────────
        new_file = _wait_for_new_pdf(download_dir, files_before)
        if new_file is None:
            log.warning(f"[{register_num}] PDF não apareceu no disco — possível erro de driver.")
            # Download travado é sintoma de driver ruim, não de bula inexistente
            return DRIVER_ERROR, None

        log.info(f"[{register_num}] Baixado → {new_file}")
        return OK, new_file

    except (TimeoutException, NoSuchElementException):
        # Botão de bula não apareceu → registro simplesmente não tem bula do paciente
        log.info(f"[{register_num}] Sem bula do paciente.")
        return NOT_FOUND, None

    except WebDriverException as e:
        # Sessão morta, browser crashou, etc — aí sim é erro de driver
        log.error(f"[{register_num}] WebDriverException: {e.msg.splitlines()[0]}")
        return DRIVER_ERROR, None


def _restart_driver(driver: webdriver.Firefox, download_dir: str) -> webdriver.Firefox:
    """Encerra o driver atual e devolve um novo."""
    log.info("Reiniciando driver…")
    quit_driver(driver)
    time.sleep(4)
    new_driver = initialize_driver(download_dir)
    log.info("Driver reiniciado com sucesso.")
    return new_driver


def run_batch(
    register_nums: list[str],
    download_dir: str,
    process_fn,
    output_dict: dict,
    restart_every: int = RESTART_EVERY,
) -> dict:
    """
    Itera sobre *register_nums* reutilizando um driver, reiniciando-o:
      - a cada *restart_every* downloads bem-sucedidos (manutenção preventiva)
      - imediatamente após *MAX_CONSECUTIVE_FAILURES* erros de driver seguidos

    NOT_FOUND  → marca no checkpoint, não tenta de novo
    DRIVER_ERROR → NÃO marca no checkpoint, reinicia driver, tenta de novo
    """
    done = load_checkpoint()
    remaining = [n for n in register_nums if n not in done]
    log.info(f"Total: {len(register_nums)} | Já feitos: {len(done)} | Restantes: {len(remaining)}")

    driver = initialize_driver(download_dir)
    success_count      = 0
    consecutive_errors = 0

    try:
        i = 0
        while i < len(remaining):
            num = remaining[i]

            # ── Reinício preventivo por volume ───────────────────────────────
            if success_count > 0 and success_count % restart_every == 0:
                log.info(f"Reinício preventivo após {success_count} downloads.")
                driver = _restart_driver(driver, download_dir)

            log.info(f"[{i+1}/{len(remaining)}] {num}…")
            status, filename = download_bula(num, driver, download_dir)

            # ── Sucesso ──────────────────────────────────────────────────────
            if status == OK:
                consecutive_errors = 0
                filepath = os.path.join(download_dir, filename)
                try:
                    data = process_fn(filepath)
                    if data:
                        output_dict[num] = data
                except Exception as e:
                    log.error(f"[{num}] Erro ao processar PDF: {e}")
                finally:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                done.add(num)
                save_checkpoint(done)
                success_count += 1
                i += 1

            # ── Bula não existe — pula e marca checkpoint ─────────────────────
            elif status == NOT_FOUND:
                consecutive_errors = 0
                log.info(f"[{num}] Sem bula — marcado no checkpoint.")
                done.add(num)
                save_checkpoint(done)
                i += 1

            # ── Erro de driver — NÃO avança, reinicia e tenta de novo ────────
            elif status == DRIVER_ERROR:
                consecutive_errors += 1
                log.warning(
                    f"[{num}] Erro de driver ({consecutive_errors}/{MAX_CONSECUTIVE_FAILURES}). "
                    f"NÃO marcado no checkpoint."
                )
                driver = _restart_driver(driver, download_dir)

                if consecutive_errors >= MAX_CONSECUTIVE_FAILURES:
                    log.error(
                        f"[{num}] {MAX_CONSECUTIVE_FAILURES} erros seguidos mesmo após reinícios. "
                        f"Pulando este número para não travar o script."
                    )
                    done.add(num)
                    save_checkpoint(done)
                    consecutive_errors = 0
                    i += 1
                # se ainda abaixo do limite: while repete com o mesmo num e driver novo

    except KeyboardInterrupt:
        log.info("Interrompido pelo usuário. Progresso salvo.")
    finally:
        quit_driver(driver)

    return output_dict