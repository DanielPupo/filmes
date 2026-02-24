from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
app.secret_key = "cineverse_secret"

API_KEY = "74ef07cf4c116a3dc0ca33b1c692d3a7"
BASE_URL = "https://api.themoviedb.org/3"


def requisicao(endpoint, params=None):
    if params is None:
        params = {}
    params["api_key"] = API_KEY
    params["language"] = "pt-BR"
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, params=params)
    return response.json()


@app.route("/")
def index():
    generos = requisicao("/genre/movie/list").get("genres", [])
    destaque = requisicao("/movie/popular").get("results", [])[0]
    top10 = requisicao("/trending/movie/week").get("results", [])[:10]
    return render_template("index.html", generos=generos, destaque=destaque, top10=top10)


@app.route("/buscar_ajax", methods=["POST"])
def buscar_ajax():
    data = request.get_json()
    pagina = data.get("pagina", 1)
    generos = data.get("generos", "")
    busca = data.get("busca", "")

    if busca:
        endpoint = "/search/movie"
        params = {"query": busca, "page": pagina}
    else:
        endpoint = "/discover/movie"
        params = {"with_genres": generos, "page": pagina, "sort_by": "popularity.desc"}

    filmes = requisicao(endpoint, params).get("results", [])
    return jsonify(filmes)


@app.route("/filme/<int:filme_id>")
def filme(filme_id):
    filme = requisicao(f"/movie/{filme_id}", {"append_to_response": "videos"})
    return render_template("filme.html", filme=filme)


if __name__ == "__main__":
    app.run(debug=True)