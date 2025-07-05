import sys
import os
import webbrowser

def gerar_html_leitura(pasta_capitulo):
    imagens = sorted([
        f for f in os.listdir(pasta_capitulo)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
    ])
    if not imagens:
        print("Nenhuma imagem encontrada na pasta:", pasta_capitulo)
        return

    imagens_js = ",\n  ".join(f'"{img}"' for img in imagens)
    html_path = os.path.join(pasta_capitulo, "leitor.html")

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<title>Leitor de Mangá</title>
<style>
  body {{
    margin: 0;
    background: #000;
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 100vh;
    color: #eee;
    user-select: none;
    overflow: hidden;
  }}

  header {{
    padding: 10px;
    font-size: 1.2em;
    text-align: center;
  }}

  #imagem-container {{
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    max-width: 900px;
    overflow: hidden;
    position: relative;
  }}

  #imagem {{
    max-width: 100%;
    max-height: 100%;
    transition: transform 0.3s ease;
    cursor: grab;
  }}

  footer {{
    padding: 10px;
    text-align: center;
  }}

  button {{
    background: #222;
    border: none;
    color: #eee;
    padding: 10px 15px;
    margin: 0 5px;
    font-size: 1em;
    border-radius: 5px;
    cursor: pointer;
    user-select: none;
    transition: background 0.3s;
  }}
  button:hover {{
    background: #555;
  }}
</style>
</head>
<body>

<header>
  <div id="pagina-atual">Página 1 / {len(imagens)}</div>
</header>

<div id="imagem-container">
  <img id="imagem" src="" alt="Página do mangá" />
</div>

<footer>
  <button id="btn-anterior">Anterior</button>
  <button id="btn-zoom-in">+</button>
  <button id="btn-zoom-out">-</button>
  <button id="btn-proximo">Próximo</button>
</footer>

<script>
  const imagens = [
  {imagens_js}
  ];

  const imgEl = document.getElementById("imagem");
  const paginaAtualEl = document.getElementById("pagina-atual");

  let idx = 0;
  let escala = 1;
  const escalaMin = 1;
  const escalaMax = 3;

  function atualizarImagem() {{
    imgEl.src = imagens[idx];
    escala = 1;
    imgEl.style.transform = `scale(${{escala}})`;
    paginaAtualEl.textContent = `Página ${{idx + 1}} / ${{imagens.length}}`;
  }}

  function zoomIn() {{
    if (escala < escalaMax) {{
      escala = Math.min(escalaMax, escala + 0.2);
      imgEl.style.transform = `scale(${{escala}})`;
    }}
  }}

  function zoomOut() {{
    if (escala > escalaMin) {{
      escala = Math.max(escalaMin, escala - 0.2);
      imgEl.style.transform = `scale(${{escala}})`;
    }}
  }}

  document.getElementById("btn-anterior").onclick = () => {{
    if (idx > 0) {{
      idx--;
      atualizarImagem();
    }}
  }};

  document.getElementById("btn-proximo").onclick = () => {{
    if (idx < imagens.length - 1) {{
      idx++;
      atualizarImagem();
    }}
  }};

  document.getElementById("btn-zoom-in").onclick = zoomIn;
  document.getElementById("btn-zoom-out").onclick = zoomOut;

  imgEl.addEventListener('wheel', (event) => {{
    event.preventDefault();
    if (event.deltaY < 0) {{
      zoomIn();
    }} else {{
      zoomOut();
    }}
  }});

  atualizarImagem();
</script>

</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML do leitor gerado em: {html_path}")
    webbrowser.open(f"file://{os.path.abspath(html_path)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python leitor.py <pasta_do_capitulo>")
        sys.exit(1)

    pasta = sys.argv[1]
    if not os.path.isdir(pasta):
        print(f"Pasta inválida: {pasta}")
        sys.exit(1)

    gerar_html_leitura(pasta)
