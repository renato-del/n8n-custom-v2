import sys
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# ==============================
# Argumento: link do processo
# ==============================
if len(sys.argv) < 2:
    print("Uso: python consulta_processo.py <link_processo>")
    sys.exit(1)

link_processo = sys.argv[1].strip()
print(f"Tentando acessar: {link_processo}")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

try:
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    # ---------------------
    # LOGIN
    # ---------------------
    driver.get("https://astrea.net.br/#/login/BR")
    time.sleep(5)

    search_box = driver.find_element(By.NAME, 'username')
    search_box.send_keys('suporte@mlrg.com.br')
    search_box.submit()

    search_box = driver.find_element(By.NAME, 'password')
    search_box.send_keys('Mlrg@2025')
    search_box.submit()

    # Confirma o login
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "nav.au-app-nav")
    ))
    print("Login concluído. Preparando para navegar para o processo.")

    # -----------------------------------
    # NAVEGAÇÃO E CAPTURA DO PROCESSO
    # -----------------------------------

    # Abre diretamente o link do processo
    driver.get(link_processo)

    # NOVO BLOCO DE ESPERA: Aguarda que o elemento principal (case-view-react) 
    # e seu conteúdo (o título H1) sejam carregados.
    print("Aguardando carregamento da página do processo...")
    
    # 1. Espera pela tag principal do conteúdo
    wait.until(EC.presence_of_element_located(
        (By.TAG_NAME, "case-view-react")
    ))
    
    # 2. Espera por um elemento específico (o título H1) para garantir que os dados dinâmicos carregaram
    element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "case-view-react h1.egmhtcs0")
    ))

    # Remove iframes de chat que possam atrapalhar (boa prática)
    try:
        driver.execute_script("""
            var frames = document.querySelectorAll('iframe[name*="intercom"]');
            frames.forEach(f => f.remove());
        """)
    except:
        pass
    
    # Captura texto de todo o componente React que contém as informações
    # É mais seguro pegar o elemento pai (case-view-react) novamente, 
    # pois ele engloba todas as informações.
    case_view_element = driver.find_element(By.TAG_NAME, "case-view-react")
    txt_element = case_view_element.text
    
    print("\n--- Conteúdo da Página do Processo ---\n")
    print(txt_element)
    print("\n--------------------------------------\n")

except TimeoutException as e:
    # Captura TimeoutExceptions
    print(f"Erro: O tempo limite foi atingido ao carregar a página do processo. {e}")
except Exception as e:
    # Captura outros erros
    print("Erro ao consultar processo:", e)

finally:
    try:
        # Deixe o time.sleep para que você possa inspecionar a página antes de fechar
        # Comente o 'time.sleep' quando estiver rodando em produção.
        # time.sleep(10)
        driver.quit() 
    except:
        pass