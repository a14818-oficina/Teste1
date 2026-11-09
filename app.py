import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from con_sql import bd
from blocklist import BLOCKLIST
from models.user import UserModel
from resources.user import UserRegister, UserLogin, UserLogout
from resources.tarefa import Tarefas, Tarefa

# variavel representar a minha aplicaçao
app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)

# Configuraçoes
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tarefas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "a_minha_palavra_secreta_para_a_minha_api_vai_ser_forte_e_longa"
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["PROPAGATE_EXCEPTIONS"] = True  # deixa o JWT devolver 401 em vez de 500

# Credenciais do admin inicial (podem vir de variáveis de ambiente)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@oficina.pt")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

bd.init_app(app)


# ---------- JWT: respostas de erro (401) ----------
@jwt.token_in_blocklist_loader
def verificar_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.revoked_token_loader
def token_revogado(jwt_header, jwt_payload):
    return {"message": "You have no access to this resource. Login please"}, 401


@jwt.unauthorized_loader
def token_em_falta(motivo):
    return {"message": "Not authenticated. Login please"}, 401


@jwt.invalid_token_loader
def token_invalido(motivo):
    return {"message": "Invalid token"}, 401


@jwt.expired_token_loader
def token_expirado(jwt_header, jwt_payload):
    return {"message": "Token expired. Login again"}, 401


# ---------- Rotas ----------
api.add_resource(UserRegister, "/registo")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(Tarefas, "/tarefas")
api.add_resource(Tarefa, "/tarefas/<int:id_tarefa>")


# ---------- Inicialização: tabelas + admin ----------
def criar_admin_inicial():
    if not UserModel.find_by_email(ADMIN_EMAIL):
        admin = UserModel(ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD, tipo="admin")
        admin.save_user()
        print(f"Admin criado: {ADMIN_EMAIL}")


with app.app_context():
    bd.create_all()        # cria as tabelas na primeira execução
    criar_admin_inicial()


if __name__ == "__main__":
    app.run(debug=True)