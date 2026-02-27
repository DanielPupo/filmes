from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests
from functools import lru_cache

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Troque por uma chave segura em produção

API_KEY = "74ef07cf4c116a3dc0ca33b1c692d3a7"
BASE_URL = "https://api.themoviedb.org/3"

@lru_cache(maxsize=128)
def get_movie_details(movie_id):
    resposta = requests.get(f"{BASE_URL}/movie/{movie_id}", params={
        "api_key": API_KEY,
        "language": "pt-BR"
    })
    return resposta.json() if resposta.status_code == 200 else None

@app.route("/")
def index():
    # Página inicial com a primeira página de filmes
    page = request.args.get('page', 1, type=int)
    catalogo_req = requests.get(f"{BASE_URL}/discover/movie", params={
        "api_key": API_KEY,
        "language": "pt-BR",
        "sort_by": "popularity.desc",
        "page": page
    })
    filmes = catalogo_req.json().get("results", [])

    # Top 10 (para exibir no topo)
    top_req = requests.get(f"{BASE_URL}/movie/popular", params={
        "api_key": API_KEY,
        "language": "pt-BR",
        "page": 1
    })
    top10 = top_req.json().get("results", [])[:10]

    return render_template("index.html", filmes=filmes, top10=top10)

@app.route("/carregar")
def carregar_mais():
    # Rota AJAX para carregar mais filmes (infinite scroll)
    page = request.args.get('page', 1, type=int)
    catalogo_req = requests.get(f"{BASE_URL}/discover/movie", params={
        "api_key": API_KEY,
        "language": "pt-BR",
        "sort_by": "popularity.desc",
        "page": page
    })
    filmes = catalogo_req.json().get("results", [])
    return jsonify(filmes)

@app.route("/top10")
def top10():
    top_req = requests.get(f"{BASE_URL}/movie/popular", params={
        "api_key": API_KEY,
        "language": "pt-BR",
        "page": 1
    })
    top10 = top_req.json().get("results", [])[:10]
    return render_template("top10.html", top10=top10)

@app.route("/favoritos")
def favoritos():
    favoritos_ids = session.get('favoritos', [])
    filmes_favoritos = []
    for movie_id in favoritos_ids:
        filme = get_movie_details(movie_id)
        if filme:
            filmes_favoritos.append(filme)
    return render_template("favoritos.html", favoritos=filmes_favoritos)

@app.route("/filme/<int:id>")
def detalhes_filme(id):
    filme = get_movie_details(id)
    if not filme:
        return "Filme não encontrado", 404
    favoritos_ids = session.get('favoritos', [])
    eh_favorito = id in favoritos_ids
    return render_template("filme.html", filme=filme, eh_favorito=eh_favorito)

@app.route("/favoritar/<int:id>", methods=['POST'])
def favoritar(id):
    favoritos = session.get('favoritos', [])
    if id in favoritos:
        favoritos.remove(id)
    else:
        favoritos.append(id)
    session['favoritos'] = favoritos
    return redirect(request.referrer or url_for('index'))

@app.route("/buscar")
def buscar():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template("buscar.html", filmes=[], query=query)
    resposta = requests.get(f"{BASE_URL}/search/movie", params={
        "api_key": API_KEY,
        "language": "pt-BR",
        "query": query,
        "page": 1
    })
    filmes = resposta.json().get("results", [])
    return render_template("buscar.html", filmes=filmes, query=query)

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def erro_interno(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)