import sys
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys # Importa Keys para usar o ENTER

# ======================
# ENTRADA DO CLIENTE VIA ARGUMENTOS
# ======================
if len(sys.argv) < 2:
    print("Uso: python procura_processo.py <nome_cliente>")
    sys.exit(1)

# Junta todos os argumentos após o nome do script (permite nomes com espaços)
nome_cliente = " ".join(sys.argv[1:]).strip()
print(f"🔍 Buscando cliente: {nome_cliente}")

# Normaliza os nomes para comparação
opcao_desejada = f"Contato {nome_cliente}".lower()
nome_cliente_normalizado = nome_cliente.lower()

# ======================
# CONFIGURAÇÃO DO NAVEGADOR
# ======================
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--window-size=1920,1080")

MAX_TRIES = 2 # Permite a busca inicial e uma segunda tentativa

try:
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    # ... (Seu código de login e navegação para 'Processos e Casos') ...
    
    # ======================
    # LOGIN NO ASTREA
    # ======================
    driver.get("https://astrea.net.br/#/login/BR")
    print("🌐 Acessando o site do Astrea...")
    
    search_box = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
    search_box.send_keys('suporte@mlrg.com.br')
    
    search_box = driver.find_element(By.NAME, 'password')
    search_box.send_keys('Mlrg@2025')
    search_box.submit()

    # ======================
    # MENU "PROCESSOS E CASOS"
    # ======================
    print("📁 Acessando menu de Processos e Casos...")
    element = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "a#folders-menu-item.au-app-nav__item")
    ))
    driver.execute_script("arguments[0].click();", element)

    # ======================
    # LIMPA TAGS DE FILTRO EXISTENTES (Mantido)
    # ======================
    try:
        remove_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'i.fa.fa-times[ng-click*="removeTag"]')
            )
        )
        print(f"🗑️ Limpando {len(remove_buttons)} filtros existentes...")
        for btn in remove_buttons:
            driver.execute_script("arguments[0].click();", btn)
        time.sleep(1) 
    except:
        print("✅ Nenhum filtro para limpar.")
        pass

    # ======================
    # LOOP DE BUSCA COM CHECAGEM
    # ======================
    processos_finais = []
    attempt = 1
    search_success = False

    while attempt <= MAX_TRIES and not search_success:
        print(f"\n--- INICIANDO TENTATIVA DE BUSCA {attempt}/{MAX_TRIES} ---")
        
        # 1. Pesquisa e Seleção do Filtro (Tentativa 1: Filtro de Contato)
        if attempt == 1:
            print(f"🔎 Pesquisando pelo contato '{nome_cliente}'...")
            search_box = driver.find_element(By.NAME, 'filter')
            search_box.clear()
            search_box.send_keys(nome_cliente)

            try:
                # Espera aparecerem as sugestões
                sugestoes = wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "li[ng-repeat='match in matches']"))
                )

                clicou = False
                for item in sugestoes:
                    texto_item = item.text.strip().lower()
                    if opcao_desejada in texto_item:
                        driver.execute_script("arguments[0].click();", item)
                        clicou = True
                        break

                if not clicou:
                    print(f"⚠️ Não foi encontrada a opção '{opcao_desejada}' na lista. Tentando busca simples na próxima.")
                    # Se não encontrou o filtro, força a próxima tentativa
                    attempt = 2
                    continue # Volta para o início do while
                else:
                    print(f"✅ Selecionado o filtro: {opcao_desejada}")

            except Exception as e:
                print(f"⚠️ Erro ao selecionar sugestão: {e}. Tentando busca simples na próxima.")
                # Se deu erro, força a próxima tentativa
                attempt = 2
                continue
                
        # 2. Pesquisa Simples (Tentativa 2: Apenas Digitar e Enter)
        elif attempt == 2:
            print(f"🔎 Tentando busca simples por '{nome_cliente}'...")
            search_box = driver.find_element(By.NAME, 'filter')
            search_box.clear()
            search_box.send_keys(nome_cliente)
            search_box.send_keys(Keys.ENTER) # Envia o Enter para forçar a busca simples

        
        # 3. Captura e Checagem dos Processos
        process_links = []
        processos_encontrados_com_cliente = 0

        try:
            # Espera até que a lista de processos esteja visível
            print("⏳ Aguardando carregamento dos processos...")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.text-with-ellipsis--2-lines.css-1r91qgs-LinkButton")
                )
            )
            time.sleep(2)  # pequena folga extra
            
            # Captura a lista
            process_links = driver.find_elements(
                By.CSS_SELECTOR,
                "a.text-with-ellipsis--2-lines.css-1r91qgs-LinkButton"
            )

        except:
            print("⚠️ Nenhum processo apareceu após a busca. Lista pode estar vazia ou a página lenta.")
            process_links = []

        
        # 4. Checa se o NOME DO CLIENTE está em algum título de processo
        if process_links:
            for link in process_links:
                process_name = link.text.lower()
                if nome_cliente_normalizado in process_name:
                    processos_encontrados_com_cliente += 1
                    break # Basta encontrar um para confirmar que a busca foi válida

            if processos_encontrados_com_cliente > 0:
                print(f"✅ Encontrados {len(process_links)} processos. Confirmação: O nome do cliente está em pelo menos um título.")
                search_success = True
                
                # Coleta final dos dados (apenas nome e link)
                for link in process_links:
                    processos_finais.append({
                        'nome': link.text,
                        'link': link.get_attribute("href")
                    })

            else:
                print(f"❌ Encontrados {len(process_links)} processos, mas o nome do cliente não está no título de NENHUM. Rebuscando...")
                # Se não encontrou o nome no título, força a próxima tentativa
                attempt += 1
                
                # Limpa a busca para a próxima tentativa
                driver.find_element(By.NAME, 'filter').clear()
                
        else:
            print("🚫 Nenhuma lista de processo retornada.")
            attempt += 1 # Vai para a próxima tentativa se não encontrou nada
            
    # ======================
    # RESULTADO FINAL
    # ======================
    print("\n" + "="*40)
    print(f"SUMÁRIO FINAL DE PROCESSOS PARA {nome_cliente.upper()}:")
    
    if processos_finais:
        print(f"Total: {len(processos_finais)} processos encontrados na última busca válida.")
        for idx, proc in enumerate(processos_finais, start=1):
            print(f"\n=== Processo {idx} ===")
            print(f"Nome: {proc['nome']}")
            print(f"Link: {proc['link']}")
    else:
        print(f"🚫 Não foi possível encontrar processos válidos para {nome_cliente} após {MAX_TRIES} tentativas.")

except Exception as e:
    print("❌ Erro ao executar o robô:", e)

finally:
    try:
        print("🧹 Encerrando o navegador...")
        driver.quit()
    except:
        pass
