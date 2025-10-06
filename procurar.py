import sys
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ======================
# ENTRADA DO CLIENTE VIA ARGUMENTOS
# ======================
# Verifica se o nome do cliente foi fornecido
if len(sys.argv) < 2:
    print("Uso: python nome_script.py <nome_cliente>")
    sys.exit(1)

# Junta todos os argumentos após o nome do script (ex.: "renato barbieri")
# Isso permite nomes com espaços.
nome_cliente = " ".join(sys.argv[1:]).strip()

# O nome do cliente NÃO deve mais ser hardcoded aqui.
# nome_cliente = "Renato Barbieri" 
opcao_desejada = f"Contato {nome_cliente}".lower()

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

try:
    driver = webdriver.Chrome(options=options)

    # Login
    driver.get("https://astrea.net.br/#/login/BR")
    time.sleep(5)

    search_box = driver.find_element(By.NAME, 'username')
    search_box.send_keys('suporte@mlrg.com.br')
    search_box.submit()

    search_box = driver.find_element(By.NAME, 'password')
    search_box.send_keys('Mlrg@2025')
    search_box.submit()

    wait = WebDriverWait(driver, 20)

    # Acessa menu Processos e Casos
    element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "a#folders-menu-item.au-app-nav__item")
    ))
    driver.execute_script("arguments[0].click();", element)

    # Remove tags se existirem
    try:
        remove_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'i.fa.fa-times[ng-click*="removeTag"]')
            )
        )
        for btn in remove_buttons:
            driver.execute_script("arguments[0].click();", btn)
    except:
        pass

    # Pesquisa só pelo nome do cliente
    search_box = driver.find_element(By.NAME, 'filter')
    search_box.clear()
    search_box.send_keys(nome_cliente)

    # Espera a lista de sugestões
    sugestoes = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "li[ng-repeat='match in matches']")
    ))

    clicou = False
    for item in sugestoes:
        texto_item = item.text.strip().lower()
        if opcao_desejada in texto_item:
            driver.execute_script("arguments[0].click();", item)
            clicou = True
            break

    if not clicou:
        print(f"⚠️ Não foi encontrada a opção '{opcao_desejada}' na lista")
    else:
        print(f"✅ Selecionado: {opcao_desejada}")
        time.sleep(5)

        # Agora captura os processos ligados ao cliente
        process_links = driver.find_elements(
            By.CSS_SELECTOR,
            "a.text-with-ellipsis--2-lines.css-1r91qgs-LinkButton"
        )

        if not process_links:
            print("Nenhum processo encontrado para:", nome_cliente)
        else:
            for idx, link in enumerate(process_links, start=1):
                process_name = link.text
                process_href = link.get_attribute("href")

                print(f"\n=== Processo {idx} ===")
                print(f"Nome: {process_name}")
                print(f"Link: {process_href}")

except Exception as e:
    print("Erro ao executar o robô:", e)

finally:
    try:
        driver.quit()
    except:
        pass

