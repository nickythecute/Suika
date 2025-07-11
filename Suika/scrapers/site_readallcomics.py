import httpx
from bs4 import BeautifulSoup
import os
import re

BASE_URL = "https://readallcomics.com"

def busca_stories(query, max_results=50):
    url = f"{BASE_URL}/?story={query}&s=&type=comic"
    print(f"Buscando em: {url}")
    
    r = httpx.get(url)
    if r.status_code != 200:
        print(f"Erro ao acessar o site (Status code: {r.status_code})")
        return []

    soup = BeautifulSoup(r.content, "html.parser")
    resultados = []

    for li in soup.find_all("li"):
        a = li.find("a", href=True, title=True)
        if a:
            href = a["href"]
            title = a["title"].strip()
            if href and title and query.lower() in title.lower():
                resultados.append((title, href))
            if len(resultados) >= max_results:
                break

    return resultados

def lista_issues(story_url):
    print(f"Listando issues de: {story_url}")
    r = httpx.get(story_url)
    if r.status_code != 200:
        print(f"Erro ao acessar a página da história (Status: {r.status_code})")
        return []

    soup = BeautifulSoup(r.content, "html.parser")
    issues = []

    for li in soup.find_all("li"):
        a = li.find("a", href=True, title=True)
        if a:
            href = a["href"]
            title = a["title"].strip()
            issues.append((title, href))

    return issues

def criar_pasta_unica(caminho_base):
    """
    Cria um caminho de pasta único: Cap_Desconhecido, Cap_Desconhecido(2), etc.
    """
    if not os.path.exists(caminho_base):
        return caminho_base

    contador = 2
    while True:
        novo_caminho = f"{caminho_base}({contador})"
        if not os.path.exists(novo_caminho):
            return novo_caminho
        contador += 1

def baixar_images(volume_url):
    print(f"Iniciando download das imagens de: {volume_url}")

    r = httpx.get(volume_url)
    if r.status_code != 200:
        print(f"Erro ao acessar o volume (Status: {r.status_code})")
        return None

    soup = BeautifulSoup(r.content, "html.parser")
    imgs = [img["src"] for img in soup.find_all("img") if img.get("src", "").startswith("http")]

    titulo_pagina = soup.title.string if soup.title else "Volume_Desconhecido Cap_Desconhecido"
    titulo_pagina = titulo_pagina.lower()

    volume = "Volume_Desconhecido"
    capitulo = "Cap_Desconhecido"

    vol_match = re.search(r'vol(?:ume)?\s*(\d+)', titulo_pagina)
    if vol_match:
        volume = f"Volume_{vol_match.group(1)}"

    cap_match = re.search(r'cap(?:ítulo)?\s*(\d+)', titulo_pagina)
    if cap_match:
        capitulo = f"Cap_{cap_match.group(1)}"

    pasta_base = os.path.join("downloads", volume, capitulo)
    pasta = criar_pasta_unica(pasta_base)
    os.makedirs(pasta)

    for i, src in enumerate(imgs, 1):
        try:
            img_data = httpx.get(src).content
            nome_base = volume_url.rstrip("/").split("/")[-1]
            path = os.path.join(pasta, f"{nome_base}_{i:03d}.jpg")
            with open(path, "wb") as f:
                f.write(img_data)
            print(f"Imagem {i} salva: {path}")
        except Exception as e:
            print(f"Erro ao baixar {src}: {e}")

    return pasta
