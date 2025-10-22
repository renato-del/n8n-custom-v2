import sys
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

# Mapeamento dos seletores CSS para os blocos de conteúdo principais
# Mantenha o seletor de histórico como o elemento PAI do bloco
SELECTORS = {
    "cabecalho": "div.col-xs-12.col-sm-7", 
    "dados_processo": "[data-testid='case-view-card']:nth-of-type(1)", 
    "historico_recente_pai": "[data-testid='case-view-card']:nth-of-type(2)", # Nome alterado para indicar que é o pai
    "recursos": "[data-testid='case-view-card']:nth-of-type(3)",
    "atividades": "[data-testid='case-view-card']:nth-of-type(4)" 
}

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

    print("Aguardando carregamento da página do processo...")
    
    # Espera que o título da página do processo esteja visível
    wait.until(EC.visibility_of_element_located(
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
    
    # === INÍCIO DA NOVA LÓGICA DE EXTRAÇÃO DE TEXTO POR BLOCO ===
    
    texto_completo = []
    
    print("Iniciando a extração de conteúdo por blocos...")

    for nome_bloco, seletor in SELECTORS.items():
        try:
            bloco_texto = ""
            
            # TRATAMENTO ESPECIAL PARA O HISTÓRICO RECENTE
            if nome_bloco == "historico_recente_pai":
                texto_completo.append("\n\n=========================\nBLOCOS: ÚLTIMOS HISTÓRICOS\n=========================\n")
                
                # 1. Encontrar o elemento pai do bloco de Histórico
                historico_pai = driver.find_element(By.CSS_SELECTOR, seletor)
                
                # 2. Encontrar TODOS os elementos de histórico individuais dentro do pai
                # O seletor busca o div interno que contém o texto de cada item de histórico
                itens_historico = historico_pai.find_elements(
                    By.CSS_SELECTOR, 
                    "p.css-16jdfqc-TextElement, p.css-1bij5tv-TextElement" # Os seletores de classe para os textos dos posts
                )
                
                if not itens_historico:
                    # Se não encontrar os elementos de texto específicos, tenta o seletor mais genérico:
                    itens_genericos = historico_pai.find_elements(By.CSS_SELECTOR, "div[data-testid='card-component']")
                    
                    if itens_genericos:
                        bloco_texto = "Conteúdo do histórico:\n"
                        for item in itens_genericos:
                            bloco_texto += f"---\n{item.text}\n"
                    else:
                        bloco_texto = historico_pai.text # Tenta o texto do pai como fallback
                else:
                    # Se encontrou os elementos de texto específicos, junta seus textos
                    for item in itens_historico:
                        bloco_texto += f"---\n{item.text}\n"

                texto_completo.append(bloco_texto)

            # TRATAMENTO PADRÃO PARA OUTROS BLOCOS
            else:
                element = driver.find_element(By.CSS_SELECTOR, seletor)
                bloco_texto = element.text
                
                texto_completo.append(f"\n\n=========================\nBLOCOS: {nome_bloco.upper().replace('_', ' ')}\n=========================\n")
                texto_completo.append(bloco_texto)

        except NoSuchElementException:
            # Captura a exceção se um elemento não for encontrado e informa o aviso
            print(f"Aviso: Bloco '{nome_bloco.upper().replace('_', ' ')}' não encontrado.")
            texto_completo.append(f"\n--- BLOCO: {nome_bloco.upper().replace('_', ' ')}: NÃO DISPONÍVEL ---")
        except Exception as e:
            print(f"Aviso: Erro inesperado ao extrair bloco '{nome_bloco.upper().replace('_', ' ')}': {e}")
            texto_completo.append(f"\n--- BLOCO: {nome_bloco.upper().replace('_', ' ')}: ERRO NA EXTRAÇÃO ---")


    # Formatar o resultado final
    resultado_final = "".join(texto_completo)
    
    # Limpeza para remover espaços duplicados e quebras de linha excessivas
    resultado_final_limpo = re.sub(r'\n\s*\n', '\n\n', resultado_final).strip()
    
    print("\n--- Conteúdo do Processo (Extração por Blocos) ---\n")
    print(resultado_final_limpo)
    print("\n------------------------------------------------\n")
    
    # === FIM DA LÓGICA DE EXTRAÇÃO DE TEXTO POR BLOCO ===


except TimeoutException as e:
    # Captura TimeoutExceptions
    print(f"Erro: O tempo limite foi atingido ao carregar a página do processo. {e}")
except Exception as e:
    # Captura outros erros
    print("Erro ao consultar processo:", e)

finally:
    try:
        # time.sleep(10)
        driver.quit() 
    except:
        pass
