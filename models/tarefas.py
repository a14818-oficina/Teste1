from con_sql import bd

ESTADOS_VALIDOS = ["Pendente", "Em curso", "Concluída"]


class TarefaModel(bd.Model):
    __tablename__ = "tarefas"
    id = bd.Column(bd.Integer, primary_key=True, autoincrement=True)
    titulo = bd.Column(bd.String(100), nullable=False)
    descricao = bd.Column(bd.Text)
    estado = bd.Column(bd.String(20), nullable=False, default="Pendente")
    utilizador_id = bd.Column(bd.Integer, bd.ForeignKey("utilizadores.id"), nullable=False)

    # Cada tarefa pertence a um único utilizador
    utilizador = bd.relationship("UserModel", back_populates="tarefas")

    def __init__(self, titulo, descricao, estado, utilizador_id):
        self.titulo = titulo
        self.descricao = descricao
        self.estado = estado
        self.utilizador_id = utilizador_id

    def json(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "estado": self.estado,
            "utilizador_id": self.utilizador_id,
        }

    @classmethod
    def find_tarefa(cls, id_tarefa):
        return cls.query.filter_by(id=id_tarefa).first()

    @classmethod
    def find_by_utilizador(cls, utilizador_id):
        return cls.query.filter_by(utilizador_id=utilizador_id).all()

    def save_tarefa(self):
        bd.session.add(self)
        bd.session.commit()

    def delete_tarefa(self):
        bd.session.delete(self)
        bd.session.commit()
    
