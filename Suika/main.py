import os
import subprocess
from scrapers import site_mangadex, site_readallcomics

fontes = {
    "mangadex": site_mangadex,
    "readallcomics": site_readallcomics,
}

def selecionar_multiplos_indices(max_index):
    entrada = input("Digite os números dos capítulos (ex: 1, 2, 5-7) ou 'all' para todos: ").strip().lower()
    
    if entrada == "all":
        return list(range(max_index))
    
    indices = set()
    partes = [p.strip() for p in entrada.split(",")]
    for parte in partes:
        if "-" in parte:
            try:
                start, end = map(int, parte.split("-"))
                for i in range(start, end + 1):
                    if 1 <= i <= max_index:
                        indices.add(i - 1)
                    else:
                        print(f"Ignorando índice inválido: {i}")
            except ValueError:
                print(f"Ignorando entrada inválida: {parte}")
        else:
            if parte.isdigit():
                i = int(parte)
                if 1 <= i <= max_index:
                    indices.add(i - 1)
                else:
                    print(f"Ignorando índice inválido: {parte}")
            else:
                print(f"Ignorando entrada inválida: {parte}")
    return sorted(indices)


def extrair_volume_capitulo(nome_issue):
    """
    Tenta extrair o volume e capítulo do título do issue.
    Exemplo de título: 'Volume 1 Capítulo 2' ou 'Vol 1 Cap 2'
    Se não conseguir, devolve valores padrão para evitar erros.
    """
    volume = "Volume_Desconhecido"
    capitulo = "Cap_Desconhecido"

    nome_issue = nome_issue.lower()

    import re

    vol_match = re.search(r'vol(?:ume)?\s*(\d+)', nome_issue)
    if vol_match:
        volume = f"Volume_{vol_match.group(1)}"
    
    cap_match = re.search(r'cap(?:ítulo)?\s*(\d+)', nome_issue)
    if cap_match:
        capitulo = f"Cap_{cap_match.group(1)}"

    return volume, capitulo


def main():
    print("Sites disponíveis:")
    nomes_fontes = list(fontes.keys())
    for i, nome in enumerate(nomes_fontes, 1):
        print(f"{i}. {nome}")

    escolha = input("Escolha um site (número ou nome): ").strip().lower()

    if escolha.isdigit():
        idx = int(escolha) - 1
        if 0 <= idx < len(nomes_fontes):
            escolha = nomes_fontes[idx]
        else:
            print("Número inválido.")
            return

    if escolha not in fontes:
        print("Fonte não encontrada.")
        return

    scraper = fontes[escolha]

    story = input("Digite o termo de busca (story): ").strip()
    achados = scraper.busca_stories(story)
    if not achados:
        print("Nenhum quadrinho encontrado.")
        return

    print("\nQuadrinhos encontrados:")
    for idx, (t, _) in enumerate(achados, 1):
        print(f"{idx}. {t}")

    try:
        sel = int(input("\nEscolha um quadrinho: ")) - 1
    except ValueError:
        print("Escolha inválida, digite um número.")
        return

    if not (0 <= sel < len(achados)):
        print("Seleção inválida.")
        return

    story_url = achados[sel][1]

    issues = scraper.lista_issues(story_url)
    if not issues:
        print("Nenhum issue encontrado.")
        return

    print("\nIssues disponíveis:")
    for idx, (t, _) in enumerate(issues, 1):
        print(f"{idx}. {t}")

    selecionados = selecionar_multiplos_indices(len(issues))
    if not selecionados:
        print("Nenhum capítulo válido selecionado.")
        return

    for sel in selecionados:
        issue_url = issues[sel][1]
        nome_issue = issues[sel][0]

        print(f"\nBaixando capítulo: {nome_issue}")
        scraper.baixar_images(issue_url)

        volume, capitulo = extrair_volume_capitulo(nome_issue)
        pasta = os.path.join("downloads", volume, capitulo)

        if not os.path.exists(pasta):
            print(f"Erro: pasta {pasta} não encontrada após download.")
            print("Verifique se a estrutura da pasta corresponde ao esperado.")
            return

        resposta = input(f"Deseja ler o capítulo baixado em {pasta}? (s/n): ").strip().lower()
        if resposta == "s":
            subprocess.run(["python", "leitor.py", pasta])
            print("Abrindo leitor e encerrando o programa.")
            return

    print("\nDownload(s) concluído(s).")

if __name__ == "__main__":
    main()
