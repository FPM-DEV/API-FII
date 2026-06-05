from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
import time
import json
import os
import subprocess
from datetime import datetime


def converter_para_float(texto):
    try:
        return float(
            texto.replace('R$', '')
                 .replace('.', '')
                 .replace(',', '.')
                 .strip()
        )
    except:
        return None


# 🔹 Configuração do Firefox (HEADLESS)
options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.add_argument("--width=1920")
options.add_argument("--height=1080")

service = Service("/usr/local/bin/geckodriver")
driver = webdriver.Firefox(service=service, options=options)

dados_formatados = []

try:
    driver.get("https://statusinvest.com.br/fundos-imobiliarios/busca-avancada")

    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="main-2"]/div[3]/div/div/div/button[2]')
        )
    ).click()

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="list-result"]/div/div[1]/div[2]/div/table')
        )
    )

    time.sleep(2)

    js_script = """
    let select = document.querySelector("#total-page-search");
    if (select) {
        select.value = select.options[select.options.length - 1].value;
        select.dispatchEvent(new Event('change'));
    }
    """
    driver.execute_script(js_script)

    time.sleep(3)

    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, '//*[@id="list-result"]/div/div[1]/div[2]/div/table/tbody/tr')
        )
    )

    linhas = driver.find_elements(
        By.XPATH,
        '//*[@id="list-result"]/div/div[1]/div[2]/div/table/tbody/tr'
    )

    print(f"\n✅ Total de fundos listados: {len(linhas)}\n")

    for linha in linhas:
        colunas = linha.find_elements(By.TAG_NAME, "td")
        textos = [col.text for col in colunas]

        if len(textos) < 14:
            continue

        try:
            cotacao = textos[1]
            ultimo_rendimento = textos[13]

            cotacao_float = converter_para_float(cotacao)
            rendimento_float = converter_para_float(ultimo_rendimento)

            if cotacao_float is not None and rendimento_float is not None and cotacao_float != 0:
                rendimento_calculado = f"{(rendimento_float / cotacao_float) * 100:.2f}"
            else:
                rendimento_calculado = "N/A"

            dados_formatados.append({
                "Ticker": textos[0].split("\n")[0],
                "Cotação": cotacao,
                "Cotistas": textos[6],
                "Liquidez média diária": textos[9],
                "P/ VP": textos[4],
                "Patrimônio líquido": textos[10],
                "VP por Cota": textos[11],
                "Yield 12 meses": textos[3],
                "Yield mensal": textos[5],
                "Último rendimento": ultimo_rendimento,
                "Último rendimento calculado": rendimento_calculado
            })

        except Exception as e:
            print(f"Erro ao processar linha: {e}")

except Exception as e:
    print("Erro geral:", e)

finally:
    driver.quit()


# 🔹 SALVAR JSON
base_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(base_dir, "resultados_fiis.json")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(dados_formatados, f, ensure_ascii=False, indent=4)

print(f"\n📁 JSON salvo em: {output_file}")


# 🔥 GIT AUTO DEPLOY

def git_deploy():
    try:
        os.chdir(base_dir)

        subprocess.run(["git", "add", "resultados_fiis.json"], check=True)

        status = subprocess.getoutput("git status --porcelain")

        if status.strip() == "":
            print("⚠️ Nenhuma mudança no JSON. Nada para enviar ao GitHub.")
            return

        subprocess.run([
            "git",
            "commit",
            "-m",
            f"update FIIs {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ], check=True)

        subprocess.run(["git", "push"], check=True)

        print("✅ GitHub atualizado com sucesso!")

    except Exception as e:
        print(f"❌ Erro no git deploy: {e}")


# 🚀 EXECUTAR DEPLOY
git_deploy()