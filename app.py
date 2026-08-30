import requests

from flask import Flask
from flask_restx import Api, Resource, fields

from database.db import db
from datetime import datetime
from models.viagem import Viagem




app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///travel_planner.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# Configuração do Swagger
api = Api(
    app,
    version="1.0",
    title="Travel Planner API",
    description="API principal para gerenciamento de viagens."
)


# Modelo usado no POST e PUT
viagem_model = api.model("Viagem", {
    "destino": fields.String(required=True),
    "data_inicio": fields.String(required=True),
    "data_fim": fields.String(required=True),
    "orcamento": fields.Float(required=True)
})


# Modelo usado no PATCH
# Os campos são opcionais porque podemos atualizar somente um deles
viagem_patch_model = api.model("ViagemPatch", {
    "destino": fields.String(required=False),
    "data_inicio": fields.String(required=False),
    "data_fim": fields.String(required=False),
    "orcamento": fields.Float(required=False)
})


# Rota inicial
@api.route("/")
class Home(Resource):

    def get(self):
        return {
            "mensagem": "Travel Planner API funcionando!"
        }, 200


# Rotas para listar e cadastrar viagens
@api.route("/viagens")
class Viagens(Resource):

    # GET - Lista todas as viagens
    def get(self):
        viagens = Viagem.query.all()

        return {
            "viagens": [viagem.to_dict() for viagem in viagens]
        }, 200

    # POST - Cadastra uma nova viagem
    @api.expect(viagem_model)
    def post(self):
        dados = api.payload

        nova_viagem = Viagem(
            destino=dados["destino"],
            data_inicio=dados["data_inicio"],
            data_fim=dados["data_fim"],
            orcamento=dados["orcamento"]
        )

        db.session.add(nova_viagem)
        db.session.commit()

        return {
            "mensagem": "Viagem cadastrada com sucesso!",
            "viagem": nova_viagem.to_dict()
        }, 201


# Rotas para uma viagem específica
@api.route("/viagens/<int:id>")
class ViagemPorId(Resource):

    # PUT - Atualiza todos os dados da viagem
    @api.expect(viagem_model)
    def put(self, id):
        viagem = db.session.get(Viagem, id)

        if not viagem:
            return {
                "mensagem": "Viagem não encontrada."
            }, 404

        dados = api.payload

        viagem.destino = dados["destino"]
        viagem.data_inicio = dados["data_inicio"]
        viagem.data_fim = dados["data_fim"]
        viagem.orcamento = dados["orcamento"]

        db.session.commit()

        return {
            "mensagem": "Viagem atualizada com sucesso!",
            "viagem": viagem.to_dict()
        }, 200

    # PATCH - Atualiza somente os campos enviados
    @api.expect(viagem_patch_model)
    def patch(self, id):
        viagem = db.session.get(Viagem, id)

        if not viagem:
            return {
                "mensagem": "Viagem não encontrada."
            }, 404

        dados = api.payload

        if "destino" in dados:
            viagem.destino = dados["destino"]

        if "data_inicio" in dados:
            viagem.data_inicio = dados["data_inicio"]

        if "data_fim" in dados:
            viagem.data_fim = dados["data_fim"]

        if "orcamento" in dados:
            viagem.orcamento = dados["orcamento"]

        db.session.commit()

        return {
            "mensagem": "Viagem atualizada parcialmente com sucesso!",
            "viagem": viagem.to_dict()
        }, 200

    # DELETE - Exclui uma viagem
    def delete(self, id):
        viagem = db.session.get(Viagem, id)

        if not viagem:
            return {
                "mensagem": "Viagem não encontrada."
            }, 404

        db.session.delete(viagem)
        db.session.commit()

        return {
            "mensagem": "Viagem excluída com sucesso!"
        }, 200


# Cria as tabelas do banco caso ainda não existam
with app.app_context():
    db.create_all()

@api.route("/viagens/<int:id>/planejamento")
class PlanejamentoViagem(Resource):

    def get(self, id):
        viagem = db.session.get(Viagem, id)

        if not viagem:
            return {
                "mensagem": "Viagem não encontrada."
            }, 404

        data_inicio = datetime.strptime(
            viagem.data_inicio,
            "%Y-%m-%d"
        )

        data_fim = datetime.strptime(
            viagem.data_fim,
            "%Y-%m-%d"
        )

        dias = (data_fim - data_inicio).days

        dados = {
            "destino": viagem.destino,
            "dias": dias,
            "orcamento": viagem.orcamento
        }

        resposta = requests.post(
            "http://127.0.0.1:5001/planejamento",
            json=dados
        )

        return resposta.json(), resposta.status_code

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )