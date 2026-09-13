from database.db import db


class IPhone(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    modelo = db.Column(db.String(120), nullable=False)
    armazenamento = db.Column(db.String(50), nullable=False)
    cor = db.Column(db.String(50), nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    moeda = db.Column(db.String(10), nullable=False)
    preco = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "modelo": self.modelo,
            "armazenamento": self.armazenamento,
            "cor": self.cor,
            "pais": self.pais,
            "moeda": self.moeda,
            "preco": self.preco
        }