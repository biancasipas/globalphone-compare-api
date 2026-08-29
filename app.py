from flask import Flask
from flask_restx import Api, Resource, fields

from database.db import db
from models.viagem import Viagem

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///travel_planner.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

api = Api(
    app,
    version="1.0",
    title="Travel Planner API",
    description="API principal para gerenciamento de viagens."
)

viagem_model = api.model("Viagem", {
    "destino": fields.String(required=True),
    "data_inicio": fields.String(required=True),
    "data_fim": fields.String(required=True),
    "orcamento": fields.Float(required=True)
})


@api.route("/")
class Home(Resource):
    def get(self):
        return {
            "mensagem": "Travel Planner API funcionando!"
        }


@api.route("/viagens")
class Viagens(Resource):

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


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)