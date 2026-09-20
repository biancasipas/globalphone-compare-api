import os

from flask import Flask
from flask_restx import Api, Resource, fields, reqparse
import requests

from database.db import db
from models.iphone import IPhone


# ============================================================
# API SECUNDÁRIA
# ============================================================

COMPARACAO_SERVICE_URL = os.getenv(
    "COMPARACAO_SERVICE_URL",
    "http://127.0.0.1:5001"
)


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)


# ============================================================
# BANCO DE DADOS
# ============================================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///globalphone.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# ============================================================
# SWAGGER
# ============================================================

api = Api(
    app,
    version="1.0",
    title="GlobalPhone Compare API",
    description=(
        "API principal para cadastro e comparação "
        "de preços de iPhones pelo mundo."
    )
)


# ============================================================
# MODELO DO SWAGGER - POST
# ============================================================

iphone_model = api.model(
    "IPhone",
    {
        "modelo": fields.String(required=True),
        "armazenamento": fields.String(required=True),
        "cor": fields.String(required=True),
        "pais": fields.String(required=True),
        "moeda": fields.String(required=True),
        "preco": fields.Float(required=True)
    }
)


# ============================================================
# CAMPOS DO PUT
# Atualização completa
# Todos os campos são obrigatórios
# ============================================================

put_parser = reqparse.RequestParser()

put_parser.add_argument(
    "modelo",
    type=str,
    required=True,
    location="form",
    help="Modelo do iPhone"
)

put_parser.add_argument(
    "armazenamento",
    type=str,
    required=True,
    location="form",
    help="Armazenamento do iPhone"
)

put_parser.add_argument(
    "cor",
    type=str,
    required=True,
    location="form",
    help="Cor do iPhone"
)

put_parser.add_argument(
    "pais",
    type=str,
    required=True,
    location="form",
    help="País onde o iPhone é vendido"
)

put_parser.add_argument(
    "moeda",
    type=str,
    required=True,
    location="form",
    help="Moeda do preço"
)

put_parser.add_argument(
    "preco",
    type=float,
    required=True,
    location="form",
    help="Preço do iPhone"
)


# ============================================================
# CAMPOS DO PATCH
# Atualização parcial
# Todos os campos são opcionais
# ============================================================

patch_parser = reqparse.RequestParser()

patch_parser.add_argument(
    "modelo",
    type=str,
    required=False,
    location="form",
    help="Novo modelo"
)

patch_parser.add_argument(
    "armazenamento",
    type=str,
    required=False,
    location="form",
    help="Novo armazenamento"
)

patch_parser.add_argument(
    "cor",
    type=str,
    required=False,
    location="form",
    help="Nova cor"
)

patch_parser.add_argument(
    "pais",
    type=str,
    required=False,
    location="form",
    help="Novo país"
)

patch_parser.add_argument(
    "moeda",
    type=str,
    required=False,
    location="form",
    help="Nova moeda"
)

patch_parser.add_argument(
    "preco",
    type=float,
    required=False,
    location="form",
    help="Novo preço"
)


# ============================================================
# ROTA INICIAL
# ============================================================

@api.route("/")
class Home(Resource):

    def get(self):

        return {
            "mensagem": "GlobalPhone Compare API funcionando!"
        }, 200


# ============================================================
# LISTAR E CADASTRAR IPHONES
# ============================================================

@api.route("/iphones")
class IPhones(Resource):

    # --------------------------------------------------------
    # GET - Lista todos os iPhones
    # --------------------------------------------------------

    def get(self):

        iphones = IPhone.query.all()

        return {
            "iphones": [
                iphone.to_dict()
                for iphone in iphones
            ]
        }, 200


    # --------------------------------------------------------
    # POST - Cadastra um novo iPhone
    # --------------------------------------------------------

    @api.expect(iphone_model)
    def post(self):

        dados = api.payload

        novo_iphone = IPhone(
            modelo=dados["modelo"],
            armazenamento=dados["armazenamento"],
            cor=dados["cor"],
            pais=dados["pais"],
            moeda=dados["moeda"].upper(),
            preco=dados["preco"]
        )

        db.session.add(novo_iphone)

        db.session.commit()

        return {
            "mensagem": "iPhone cadastrado com sucesso!",
            "iphone": novo_iphone.to_dict()
        }, 201


# ============================================================
# ALTERAR E EXCLUIR IPHONE
# ============================================================

@api.route("/iphones/<int:id>")
class IPhonePorId(Resource):


    # ========================================================
    # PUT
    # Atualiza TODOS os campos
    # ========================================================

    @api.expect(put_parser)
    def put(self, id):

        iphone = db.session.get(IPhone, id)

        if not iphone:

            return {
                "mensagem": "iPhone não encontrado."
            }, 404


        # Pega os campos digitados no Swagger
        dados = put_parser.parse_args()


        # Atualiza todos os dados
        iphone.modelo = dados["modelo"]

        iphone.armazenamento = dados["armazenamento"]

        iphone.cor = dados["cor"]

        iphone.pais = dados["pais"]

        iphone.moeda = dados["moeda"].upper()

        iphone.preco = dados["preco"]


        db.session.commit()


        return {
            "mensagem": "iPhone atualizado com sucesso!",
            "iphone": iphone.to_dict()
        }, 200


    # ========================================================
    # PATCH
    # Atualiza SOMENTE os campos preenchidos
    # ========================================================

    @api.expect(patch_parser)
    def patch(self, id):

        iphone = db.session.get(IPhone, id)

        if not iphone:

            return {
                "mensagem": "iPhone não encontrado."
            }, 404


        # Pega os campos preenchidos
        dados = patch_parser.parse_args()


        # ----------------------------------------------------
        # MODELO
        # ----------------------------------------------------

        if dados["modelo"] is not None:

            iphone.modelo = dados["modelo"]


        # ----------------------------------------------------
        # ARMAZENAMENTO
        # ----------------------------------------------------

        if dados["armazenamento"] is not None:

            iphone.armazenamento = dados["armazenamento"]


        # ----------------------------------------------------
        # COR
        # ----------------------------------------------------

        if dados["cor"] is not None:

            iphone.cor = dados["cor"]


        # ----------------------------------------------------
        # PAÍS
        # ----------------------------------------------------

        if dados["pais"] is not None:

            iphone.pais = dados["pais"]


        # ----------------------------------------------------
        # MOEDA
        # ----------------------------------------------------

        if dados["moeda"] is not None:

            iphone.moeda = dados["moeda"].upper()


        # ----------------------------------------------------
        # PREÇO
        # ----------------------------------------------------

        if dados["preco"] is not None:

            iphone.preco = dados["preco"]


        db.session.commit()


        return {
            "mensagem": (
                "iPhone atualizado parcialmente com sucesso!"
            ),
            "iphone": iphone.to_dict()
        }, 200


    # ========================================================
    # DELETE
    # ========================================================

    def delete(self, id):

        iphone = db.session.get(IPhone, id)

        if not iphone:

            return {
                "mensagem": "iPhone não encontrado."
            }, 404


        db.session.delete(iphone)

        db.session.commit()


        return {
            "mensagem": "iPhone excluído com sucesso!"
        }, 200


# ============================================================
# API EXTERNA - COTAÇÃO DE MOEDAS
# ============================================================

@api.route("/cotacao/<moeda>")
class Cotacao(Resource):

    def get(self, moeda):

        moeda = moeda.upper()


        # ----------------------------------------------------
        # REAL NÃO PRECISA SER CONVERTIDO
        # ----------------------------------------------------

        if moeda == "BRL":

            return {
                "moeda_origem": "BRL",
                "moeda_destino": "BRL",
                "cotacao": 1.0
            }, 200


        # ----------------------------------------------------
        # API DE COTAÇÃO
        # ----------------------------------------------------

        url = "https://api.frankfurter.dev/v2/rates"

        parametros = {
            "base": moeda,
            "quotes": "BRL"
        }


        try:

            resposta = requests.get(
                url,
                params=parametros,
                timeout=10
            )


            resposta.raise_for_status()


            dados = resposta.json()


            if not dados:

                return {
                    "mensagem": "Cotação não encontrada."
                }, 404


            cotacao = dados[0]["rate"]


            return {
                "moeda_origem": moeda,
                "moeda_destino": "BRL",
                "cotacao": cotacao
            }, 200


        except requests.RequestException:

            return {
                "mensagem": (
                    "Erro ao consultar a API de cotação."
                )
            }, 502


# ============================================================
# PREÇO DO IPHONE CONVERTIDO PARA REAL
# ============================================================

@api.route("/iphones/<int:id>/preco-convertido")
class PrecoConvertido(Resource):

    def get(self, id):


        # ----------------------------------------------------
        # BUSCA IPHONE NO BANCO
        # ----------------------------------------------------

        iphone = db.session.get(IPhone, id)


        if not iphone:

            return {
                "mensagem": "iPhone não encontrado."
            }, 404


        moeda = iphone.moeda.upper()


        # ====================================================
        # SE JÁ FOR BRL
        # ====================================================

        if moeda == "BRL":

            return {
                "iphone": iphone.to_dict(),
                "cotacao": 1.0,
                "preco_em_reais": iphone.preco
            }, 200


        # ====================================================
        # CONSULTA A API EXTERNA DE CÂMBIO
        # ====================================================

        url_cotacao = (
            "https://api.frankfurter.dev/v2/rates"
        )


        parametros = {
            "base": moeda,
            "quotes": "BRL"
        }


        try:

            resposta_cotacao = requests.get(
                url_cotacao,
                params=parametros,
                timeout=10
            )


            resposta_cotacao.raise_for_status()


            dados_cotacao = resposta_cotacao.json()


            if not dados_cotacao:

                return {
                    "mensagem": (
                        "Não foi possível obter a cotação."
                    )
                }, 502


            cotacao = dados_cotacao[0]["rate"]


        except requests.RequestException:

            return {
                "mensagem": (
                    "Erro ao consultar a API externa "
                    "de câmbio."
                )
            }, 502


        # ====================================================
        # ENVIA PARA A API SECUNDÁRIA
        # ====================================================

        dados_conversao = {
            "preco": iphone.preco,
            "cotacao": cotacao,
            "moeda": moeda
        }


        try:

            resposta_secundaria = requests.post(
                f"{COMPARACAO_SERVICE_URL}/converter-preco",
                json=dados_conversao,
                timeout=10
            )


            resposta_secundaria.raise_for_status()


            resultado = resposta_secundaria.json()


        except requests.RequestException:

            return {
                "mensagem": (
                    "Erro ao comunicar com "
                    "a API Secundária."
                )
            }, 502


        # ====================================================
        # RESPOSTA FINAL
        # ====================================================

        return {
            "iphone": iphone.to_dict(),
            "cotacao": cotacao,
            "conversao": resultado
        }, 200


# ============================================================
# COMPARAR DOIS IPHONES
# ============================================================

@api.route("/iphones/comparar/<int:id1>/<int:id2>")
class CompararIPhones(Resource):

    def get(self, id1, id2):


        # ----------------------------------------------------
        # BUSCA OS DOIS IPHONES
        # ----------------------------------------------------

        iphone1 = db.session.get(IPhone, id1)

        iphone2 = db.session.get(IPhone, id2)


        if not iphone1 or not iphone2:

            return {
                "mensagem": (
                    "Um dos iPhones não foi encontrado."
                )
            }, 404


        # ====================================================
        # FUNÇÃO PARA CONVERTER PARA REAL
        # ====================================================

        def converter_para_real(iphone):


            moeda = iphone.moeda.upper()


            # ------------------------------------------------
            # SE JÁ FOR REAL
            # ------------------------------------------------

            if moeda == "BRL":

                return iphone.preco


            # ------------------------------------------------
            # CONSULTA COTAÇÃO
            # ------------------------------------------------

            url = "https://api.frankfurter.dev/v2/rates"


            parametros = {
                "base": moeda,
                "quotes": "BRL"
            }


            resposta_cotacao = requests.get(
                url,
                params=parametros,
                timeout=10
            )


            resposta_cotacao.raise_for_status()


            dados_cotacao = resposta_cotacao.json()


            if not dados_cotacao:

                raise requests.RequestException(
                    "Cotação não encontrada."
                )


            cotacao = dados_cotacao[0]["rate"]


            # ------------------------------------------------
            # ENVIA PARA API SECUNDÁRIA
            # ------------------------------------------------

            dados_conversao = {
                "preco": iphone.preco,
                "cotacao": cotacao,
                "moeda": moeda
            }


            resposta_secundaria = requests.post(
                (
                    f"{COMPARACAO_SERVICE_URL}"
                    "/converter-preco"
                ),
                json=dados_conversao,
                timeout=10
            )


            resposta_secundaria.raise_for_status()


            resultado_conversao = (
                resposta_secundaria.json()
            )


            return (
                resultado_conversao["preco_em_reais"]
            )


        # ====================================================
        # REALIZA A COMPARAÇÃO
        # ====================================================

        try:

            preco1_real = converter_para_real(
                iphone1
            )


            preco2_real = converter_para_real(
                iphone2
            )


            dados_comparacao = {
                "pais_1": iphone1.pais,
                "preco_1": preco1_real,
                "pais_2": iphone2.pais,
                "preco_2": preco2_real
            }


            resposta_comparacao = requests.post(
                (
                    f"{COMPARACAO_SERVICE_URL}"
                    "/comparar-precos"
                ),
                json=dados_comparacao,
                timeout=10
            )


            resposta_comparacao.raise_for_status()


            resultado = resposta_comparacao.json()


            return {
                "iphone_1": iphone1.to_dict(),
                "preco_em_reais_1": preco1_real,
                "iphone_2": iphone2.to_dict(),
                "preco_em_reais_2": preco2_real,
                "comparacao": resultado
            }, 200


        except requests.RequestException:

            return {
                "mensagem": (
                    "Erro ao realizar a comparação."
                )
            }, 502


# ============================================================
# CRIA AS TABELAS DO BANCO
# ============================================================

with app.app_context():

    db.create_all()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
