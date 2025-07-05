import httpx, os, zipfile, shutil
from concurrent.futures import ThreadPoolExecutor

BASE_API = "https://api.mangadex.org"

def busca_stories(query, max_results=50):
    r = httpx.get(f"{BASE_API}/manga", params={"title": query})
    if r.status_code != 200:
        print(f"Erro ao buscar mangás: {r.status_code}")
        return []

    mangas = r.json().get("data", [])
    resultados = []
    for manga in mangas[:max_results]:
        manga_id = manga["id"]
        title = manga["attributes"]["title"].get("en") or "Sem título"
        resultados.append((title, manga_id))
    return resultados

def lista_issues(manga_id, idioma="en", max_results=100):
    endpoint = f"{BASE_API}/manga/{manga_id}/feed"
    params = {
        "translatedLanguage[]": idioma,
        "order[chapter]": "asc",
        "limit": max_results
    }
    r = httpx.get(endpoint, params=params)
    if r.status_code != 200:
        print(f"Erro ao obter capítulos: {r.status_code}")
        return []

    data = r.json().get("data", [])
    capitulos = []
    for cap in data:
        numero = cap["attributes"].get("chapter", "???")
        volume = cap["attributes"].get("volume", "0")
        title = f"Vol {volume} - Cap {numero}"
        capitulos.append((title, cap))  # cap é o dicionário original para uso no download
    return capitulos

def baixar_images(capitulo, pasta="downloads", formato_imagem="jpg"):
    capitulo_id = capitulo["id"]
    capitulo_number = capitulo["attributes"].get("chapter", "???")
    volume = capitulo["attributes"].get("volume", "0")

    # pegar dados de imagem
    r = httpx.get(f"{BASE_API}/at-home/server/{capitulo_id}")
    if r.status_code != 200:
        print(f"Erro ao acessar imagens: {r.status_code}")
        return

    data = r.json()
    base_url = data["baseUrl"]
    hash_ = data["chapter"]["hash"]
    pages = data["chapter"]["data"]

    volume_dir = os.path.join(pasta, f"Volume_{volume}")
    capitulo_dir = os.path.join(volume_dir, f"Cap_{capitulo_number}")
    os.makedirs(capitulo_dir, exist_ok=True)

    print(f"Baixando Capítulo {capitulo_number}...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        session = httpx.Client()
        futures = []
        for page in pages:
            url = f"{base_url}/data/{hash_}/{page}"
            path = os.path.join(capitulo_dir, os.path.basename(page))
            futures.append(executor.submit(download_image, session, url, path))

        for future in futures:
            if not future.result():
                print("Erro em uma das imagens.")

    if formato_imagem == "cbz":
        criar_cbz(capitulo_dir)
        shutil.rmtree(capitulo_dir)

def download_image(session, url, path, max_retries=5):
    for attempt in range(max_retries):
        r = session.get(url)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            return True
    print(f"Falha ao baixar: {url}")
    return False

def criar_cbz(capitulo_dir):
    cbz_path = f"{capitulo_dir}.cbz"
    with zipfile.ZipFile(cbz_path, 'w') as cbz:
        for root, _, files in os.walk(capitulo_dir):
            for file in files:
                cbz.write(os.path.join(root, file), arcname=file)
    print(f"CBZ criado: {cbz_path}")
