from con_sql import bd


class UserModel(bd.Model):
    __tablename__ = "utilizadores"

    id = bd.Column(bd.Integer, primary_key=True)
    username = bd.Column(bd.String(80), nullable=False)
    email = bd.Column(bd.String(120), unique=True, nullable=False)
    password = bd.Column(bd.String(255), nullable=False)
    tipo = bd.Column(bd.String(20), nullable=False, default="utilizador")

    tarefas = bd.relationship(
        "TarefaModel",
        back_populates="utilizador",
        cascade="all, delete-orphan"
    )

    def __init__(self, username, email, password, tipo="utilizador"):
        self.username = username
        self.email = email
        self.password = password
        self.tipo = tipo

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "tipo": self.tipo,
        }

    def verificar_password(self, password):
        return self.password == password

    @classmethod
    def find_user(cls, id_user):
        return cls.query.filter_by(id=id_user).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def save_user(self):
        bd.session.add(self)
        bd.session.commit()

    def delete_user(self):
        bd.session.delete(self)
        bd.session.commit()