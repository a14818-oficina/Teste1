from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from models.user import UserModel
from blocklist import BLOCKLIST


class UserRegister(Resource):
    # Só aceita username, email e password. O "tipo" nunca vem do pedido.
    argumentos = reqparse.RequestParser()
    argumentos.add_argument("username", type=str, required=True, help="Username obrigatorio")
    argumentos.add_argument("email", type=str, required=True, help="Email obrigatorio")
    argumentos.add_argument("password", type=str, required=True, help="Password obrigatoria")

    def post(self):
        dados = UserRegister.argumentos.parse_args()  # Dicionario

        if not dados["username"].strip() or not dados["email"].strip() or not dados["password"]:
            return {"message": "Username, email and password cannot be empty"}, 400

        if UserModel.find_by_email(dados["email"]):
            return {"message": "User with this email already exists"}, 400

        novo_user = UserModel(dados["username"], dados["email"], dados["password"],
                              tipo="utilizador")  # sempre utilizador
        novo_user.save_user()
        return novo_user.json(), 201


class UserLogin(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument("email", type=str, required=True, help="Email obrigatorio")
    argumentos.add_argument("password", type=str, required=True, help="Password obrigatoria")

    def post(self):
        dados = UserLogin.argumentos.parse_args()
        user = UserModel.find_by_email(dados["email"])

        if user and user.verificar_password(dados["password"]):
            # identity = id (string) | claim "tipo" = tipo de acesso
            token = create_access_token(identity=str(user.id),
                                        additional_claims={"tipo": user.tipo})
            return {"access_token": token}, 200
        return {"message": "Email or password invalid!"}, 401


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()["jti"]  # Identificador do token
        BLOCKLIST.add(jwt_id)
        return {"message": "User logged out successfully"}, 200