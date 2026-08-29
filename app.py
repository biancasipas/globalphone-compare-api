from flask import Flask
from flask_restx import Api, Resource

app = Flask(__name__)

api = Api(
    app,
    version="1.0",
    title="Travel Planner API",
    description="API principal para gerenciamento de viagens."
)


@api.route("/")
class Home(Resource):
    def get(self):
        return {
            "mensagem": "Travel Planner API funcionando!"
        }


if __name__ == "__main__":
    app.run(debug=True)