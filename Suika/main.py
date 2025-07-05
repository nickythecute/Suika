from scrapers import site_mangadex, site_readallcomics

fontes = {
    "mangadex": site_mangadex,
    "readallcomics": site_readallcomics,
}

def selecionar_multiplos_indices(max_index):
    entrada = input("Digite os números dos capítulos (ex: 1, 2, 5-7): ")
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
        scraper.baixar_images(issue_url)

if __name__ == "__main__":
    main()
