from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.tarefas import TarefaModel, ESTADOS_VALIDOS


def utilizador_atual():
    """Devolve (id, e_admin) a partir do token JWT."""
    return int(get_jwt_identity()), get_jwt().get("tipo") == "admin"


def estado_invalido(estado):
    return estado is not None and estado not in ESTADOS_VALIDOS


MSG_ESTADO = {"message": f"Estado invalido. Use um de: {ESTADOS_VALIDOS}"}


class Tarefas(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument("titulo", type=str, required=True, help="Titulo obrigatorio")
    argumentos.add_argument("descricao", type=str)
    argumentos.add_argument("estado", type=str)

    @jwt_required()
    def get(self):
        user_id, e_admin = utilizador_atual()
        if e_admin:
            tarefas = TarefaModel.query.all()                   # admin vê todas
        else:
            tarefas = TarefaModel.find_by_utilizador(user_id)   # utilizador só as suas
        return {"tarefas": [t.json() for t in tarefas]}, 200

    @jwt_required()
    def post(self):
        user_id, _ = utilizador_atual()
        dados = Tarefas.argumentos.parse_args()

        if not dados["titulo"].strip():
            return {"message": "Titulo cannot be empty"}, 400

        estado = dados["estado"] or "Pendente"
        if estado_invalido(estado):
            return MSG_ESTADO, 400

        # Fica automaticamente associada ao utilizador autenticado
        nova = TarefaModel(dados["titulo"], dados["descricao"], estado, user_id)
        nova.save_tarefa()
        return nova.json(), 201


class Tarefa(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument("titulo", type=str)
    argumentos.add_argument("descricao", type=str)
    argumentos.add_argument("estado", type=str)

    @staticmethod
    def obter_com_permissao(id_tarefa):
        """Devolve (tarefa, erro). Valida 404 e 403."""
        user_id, e_admin = utilizador_atual()
        tarefa = TarefaModel.find_tarefa(id_tarefa)
        if not tarefa:
            return None, ({"message": "Task not found"}, 404)
        if not e_admin and tarefa.utilizador_id != user_id:
            return None, ({"message": "You have no permission to access this task"}, 403)
        return tarefa, None

    @jwt_required()
    def get(self, id_tarefa):
        tarefa, erro = Tarefa.obter_com_permissao(id_tarefa)
        if erro:
            return erro
        return tarefa.json(), 200

    @jwt_required()
    def put(self, id_tarefa):
        tarefa, erro = Tarefa.obter_com_permissao(id_tarefa)
        if erro:
            return erro

        dados = Tarefa.argumentos.parse_args()
        if all(v is None for v in dados.values()):
            return {"message": "Nothing to update"}, 400
        if estado_invalido(dados["estado"]):
            return MSG_ESTADO, 400
        if dados["titulo"] is not None and not dados["titulo"].strip():
            return {"message": "Titulo cannot be empty"}, 400

        # Atualiza apenas os campos enviados; o dono da tarefa não muda
        for campo, valor in dados.items():
            if valor is not None:
                setattr(tarefa, campo, valor)
        tarefa.save_tarefa()
        return tarefa.json(), 200

    @jwt_required()
    def delete(self, id_tarefa):
        tarefa, erro = Tarefa.obter_com_permissao(id_tarefa)
        if erro:
            return erro
        tarefa.delete_tarefa()
        return {"message": f"Task with id {id_tarefa} deleted"}, 200