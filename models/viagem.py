from database.db import db


class Viagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destino = db.Column(db.String(120), nullable=False)
    data_inicio = db.Column(db.String(10), nullable=False)
    data_fim = db.Column(db.String(10), nullable=False)
    orcamento = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "destino": self.destino,
            "data_inicio": self.data_inicio,
            "data_fim": self.data_fim,
            "orcamento": self.orcamento
        }