"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, TipoServicio, EvaluacionProveedor, OrdenServicio, TiposServicio, TokenBlocklist, SolicitudEdo
#from models import Person

app = Flask(__name__)
ACCESS_EXPIRES = timedelta(hours=1)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"]=os.environ.get("horse cat mouse")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
jwt = JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
@app.route('/user/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_user(user_id = None):
	if request.method == 'GET':
		if user_id  is None:
			users = User.query.all()
			users = list(map(lambda user: user.serialize(), users))
			return jsonify(users),200
		else:
			user = User.query.filter_by(id=user_id).first()
			if user is not None:
				return jsonify(user.serialize()),200
			else:
				return jsonify({
					"msg": "user not found"
				}), 404
	if request.method == 'PUT':
		body = request.json
		if not body.get("email"):
			return jsonify({
				"msg": "something happened, try again"				
			}), 400

		if not body.get("password"):
			return jsonify({
				"msg": "something happened, try again"				
			}), 400
			
		user_update = User.query.filter_by(id=user_id).first()
		
		if user_update is None:
			return jsonify({
				"msg": "User not found"
			}), 404

		user = User(email=body["email"], password=body["password"])	
		try:
		
			user_update.email = body.get("email")
			db.session.commit()
			return jsonify(user.serialize()), 201
		except Exception as error:
			db.session.rollback()
			return jsonify(error.args)
		
		
	if request.method == 'DELETE':		
		user_delete = User.query.filter_by(id=user_id).first()
		if user_delete is None:
			return jsonify({
				"msg": "User not found"
			}), 404
			
		db.session.delete(user_delete)
		
		try: 
			db.session.commit()
			return jsonify([]), 204
		except Exception as error:
			db.session.rollback()
			return jsonify(error.args)

@app.route('/user', methods=['POST'])
def handle_other_user():
	body = request.json
	
	if not body.get("email"):
		return jsonify({
			"msg": "something happened, try again"
		}), 400
		
	user = User(email=body["email"], password=body["password"], nombre=body["nombre"], fecha_registro=body["fecha_registro"], tipo_usuario=body["tipo_usuario"])
	try:
		db.session.add(user)
		db.session.commit()
		return jsonify(user.serialize()), 201
	
	except Exception as error:
		db.session.rollback()
		return jsonify(error.args), 500
		
@app.route('/login', methods=['POST'])
def handle_login():
	email=request.json.get("email", None)
	password=request.json.get("password", None)

	if email is not  None and password is not None:
		user = User.query.filter_by(email=email, password=password).one_or_none()
		if user is not None:
			print(user.id)
			create_token=create_access_token(identity=user.id)
			return jsonify(
				{
					"token":create_token,
					"user_id":user.id,
					"email":user.email

				}
			)
		else:
			return jsonify({
			"msg": "Not Found"
		}), 404

	else:
		return jsonify({
			"msg": "something happened, try again"
		}), 400	


@app.route('/agregar', methods=['POST'])
# @app.route('/proveedores/<string:nature>/<int:name_id>', methods=['POST'])
@jwt_required()
def handle_add_servicio():
# def handle_add_favorite(nature, name_id):
	body=request.json
	body_name=body.get("nombre_tipo_sub_servicio", None)
# creo que no hace falta, [update] lo que no es *****
#	body_nature=body.get("favorite_nature", None)

	if body_name is not  None:
		user = get_jwt_identity()
		user_status = User.query.filter_by(id=user).one_or_none()

		if user is not None:
					tipo_servicio= TipoServicio.query.filter_by(nombre_tipo_sub_servicio=body_name, proveedor_id=user).first()
					if tipo_servicio is not None:
							return jsonify({
								"msg":"El servicio ya existe en tu perfil!"
							})
					else:
						servicio = TipoServicio(nombre_tipo_servicio=body["nombre_tipo_servicio"], nombre_tipo_sub_servicio=body["nombre_tipo_sub_servicio"],detalle_tipo_servicio=body["detalle_tipo_servicio"], proveedor_id=user )	
						try:
							db.session.add(servicio)
							db.session.commit()
							print(servicio)
							return jsonify(servicio.serialize()), 201
						except Exception as error:
							db.session.rollback()
							return jsonify(error.args), 500
		else:
				return jsonify({
								"msg": "Por favor entra en tu usuario!"
								}), 400
	else:
		return jsonify({
						"msg": "Algo paso, intentalo nuevamente [bad body format]"
						}), 400

@app.route('/proveedores/', methods=['GET'])
#@app.route('/proveedores/<int:user_id>', methods=['GET'])
@app.route('/proveedores/<string:tipo_servicio>', methods=['GET'])
def handle_proveedores(tipo_servicio = None):
	if request.method == 'GET':
		if tipo_servicio  is None:
			servicios = TipoServicio.query.all()
			servicios = list(map(lambda servicio: servicio.serialize(), servicios))
			return jsonify(servicios),200
		else:
			#servicios = TipoServicio.query.filter_by(proveedor_id=user_id).all()
			servicios = TipoServicio.query.filter_by(nombre_tipo_servicio=tipo_servicio).all()
			servicios = list(map(lambda servicio: servicio.serialize(), servicios))
			print(servicios)
			if servicios is not None:
				return jsonify(servicios),200
			else:
				return jsonify({
					"msg": "user not found"
				}), 404



@app.route('/editar_servicio/', methods=['PUT', 'DELETE'])
@jwt_required()
def handle_edit_servicio(user_id = None):
	user = get_jwt_identity()
	body = request.json
	body_name=body.get("nombre_tipo_sub_servicio", None)

	if request.method == 'PUT':
		if not body.get("nombre_tipo_sub_servicio"):
			return jsonify({
				"msg": "something happened, try again"
			}), 400

		if not body.get("nombre_tipo_servicio"):
			return jsonify({
				"msg": "something happened, try again"
			}), 400

		if not body.get("detalle_tipo_servicio"):
			return jsonify({
				"msg": "something happened, try again"
			}), 400


		service_update = TipoServicio.query.filter_by(nombre_tipo_sub_servicio=body_name, proveedor_id=user).first()

		if service_update is None:
			return jsonify({
				"msg": "No se encuentra el servicio"
			}), 404

		servicio = TipoServicio(nombre_tipo_servicio=body["nombre_tipo_servicio"], nombre_tipo_sub_servicio=body["nombre_tipo_sub_servicio"],detalle_tipo_servicio=body["detalle_tipo_servicio"], proveedor_id=user )
		
		try:

			service_update.nombre_tipo_servicio = body.get("nombre_tipo_servicio")
			service_update.nombre_tipo_sub_servicio = body.get("nombre_tipo_sub_servicio")
			service_update.detalle_tipo_servicio = body.get("detalle_tipo_servicio")
			db.session.commit()
			return jsonify(user.serialize()), 201
		except Exception as error:
			db.session.rollback()
			return jsonify(error.args)


	if request.method == 'DELETE':		
		service_delete = TipoServicio.query.filter_by(nombre_tipo_sub_servicio=body_name, proveedor_id=user).first()
		if service_delete is None:
			return jsonify({
				"msg": "No se encuentra el servicio"
			}), 404
			
		db.session.delete(service_delete)
		
		try: 
			db.session.commit()
			return jsonify([]), 204
		except Exception as error:
			db.session.rollback()
			return jsonify(error.args)

# A PARTIR DE ACA SE TRABAJA EN LA CREACION DE ORDENES DE SERVICIO

@app.route('/contratar', methods=['POST'])
# @app.route('/proveedores/<string:nature>/<int:name_id>', methods=['POST'])
@jwt_required()
def handle_add_orden():
# def handle_add_favorite(nature, name_id):
	body=request.json
	body_service=body.get("nombre_tipo_servicio", None)
	body_proveedor=body.get("nombre_proveedor", None)
# creo que no hace falta, [update] lo que no es *****
#	body_nature=body.get("favorite_nature", None)

	if body_service is not  None:
		user = get_jwt_identity()
		cliente_asignado = User.query.filter_by(id=user).first()
		proveedor_asignado = User.query.filter_by(nombre=body_proveedor).first()
		servicio = TipoServicio.query.filter_by(nombre_tipo_servicio=body_service,  proveedor_id=proveedor_asignado.id ).first()

		if user is not None:
					orden_servicio= OrdenServicio.query.filter_by(detalle_servicio_id=servicio.id, cliente_id=cliente_asignado.id, proveedor_id=proveedor_asignado.id).first()
					print(orden_servicio)
					if orden_servicio is not None:
							return jsonify({
								"msg":"La orden por este servicio ya existe en tu perfil!"
							})
					else:
						orden = OrdenServicio(detalle_servicio_id=servicio.id, proveedor_id=proveedor_asignado.id, cliente_id=cliente_asignado.id)	
						print(orden)
						try:
							db.session.add(orden)
							db.session.commit()
							return jsonify(orden.serialize()), 201
						except Exception as error:
							db.session.rollback()
							return jsonify(error.args), 500
		else:
				return jsonify({
								"msg": "Por favor entra en tu usuario!"
								}), 400
	else:
		return jsonify({
						"msg": "Algo paso, intentalo nuevamente [bad body format]"
						}), 400

# @app.route('/ordenes/', methods=['GET'])
# @app.route('/orden/<int:user_id>', methods=['GET'])
# def handle_proveedores(user_id = None):
# 	if request.method == 'GET':
# 		if user_id  is None:
# 			servicios = TipoServicio.query.all()
# 			servicios = list(map(lambda servicio: servicio.serialize(), servicios))
# 			return jsonify(servicios),200
# 		else:
# 			servicios = TipoServicio.query.filter_by(proveedor_id=user_id).all()
# 			servicios = list(map(lambda servicio: servicio.serialize(), servicios))
# 			print(servicios)
# 			if servicios is not None:
# 				return jsonify(servicios),200
# 			else:
# 				return jsonify({
# 					"msg": "user not found"
# 				}), 404



# @app.route('/editar_orden/', methods=['PUT', 'DELETE'])
# @jwt_required()
# def handle_edit_servicio(user_id = None):
# 	user = get_jwt_identity()
# 	body = request.json
# 	body_name=body.get("nombre_tipo_sub_servicio", None)

# 	if request.method == 'PUT':
# 		if not body.get("nombre_tipo_sub_servicio"):
# 			return jsonify({
# 				"msg": "something happened, try again"
# 			}), 400

# 		if not body.get("nombre_tipo_servicio"):
# 			return jsonify({
# 				"msg": "something happened, try again"
# 			}), 400

# 		if not body.get("detalle_tipo_servicio"):
# 			return jsonify({
# 				"msg": "something happened, try again"
# 			}), 400


# 		service_update = TipoServicio.query.filter_by(nombre_tipo_sub_servicio=body_name, proveedor_id=user).first()

# 		if service_update is None:
# 			return jsonify({
# 				"msg": "No se encuentra el servicio"
# 			}), 404

# 		servicio = TipoServicio(nombre_tipo_servicio=body["nombre_tipo_servicio"], nombre_tipo_sub_servicio=body["nombre_tipo_sub_servicio"],detalle_tipo_servicio=body["detalle_tipo_servicio"], proveedor_id=user )
		
# 		try:

# 			service_update.nombre_tipo_servicio = body.get("nombre_tipo_servicio")
# 			service_update.nombre_tipo_sub_servicio = body.get("nombre_tipo_sub_servicio")
# 			service_update.detalle_tipo_servicio = body.get("detalle_tipo_servicio")
# 			db.session.commit()
# 			return jsonify(user.serialize()), 201
# 		except Exception as error:
# 			db.session.rollback()
# 			return jsonify(error.args)

# HABILITAR EL BORRADO
# 	if request.method == 'DELETE':		
# 		service_delete = TipoServicio.query.filter_by(nombre_tipo_sub_servicio=body_name, proveedor_id=user).first()
# 		if service_delete is None:
# 			return jsonify({
# 				"msg": "No se encuentra el servicio"
# 			}), 404
			
# 		db.session.delete(service_delete)
		
# 		try: 
# 			db.session.commit()
# 			return jsonify([]), 204
# 		except Exception as error:
# 			db.session.rollback()
# 			return jsonify(error.args)


@app.route('/servicios/', methods=['GET'])

def handle_tipo_servicios():
	if request.method == 'GET':
			servicios = list(TiposServicio)
			if servicios is not None:
				return jsonify(servicios),200
			else:
				return jsonify({
					"msg": "user not found"
				}), 404

@app.route("/logout", methods=["DELETE"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify(msg="JWT revoked")


# A blocklisted access token will not be able to access this any more
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    return jsonify(hello="world")



@app.route('/solicitud_status', methods=['POST'])
# @app.route('/proveedores/<string:nature>/<int:name_id>', methods=['POST'])
@jwt_required()
def handle_solicitud_servicios():
# def handle_add_favorite(nature, name_id):
	body=request.json
	body_name=body.get("num_ref", None)
# creo que no hace falta, [update] lo que no es *****
#	body_nature=body.get("favorite_nature", None)

	if body_name is not  None:
		user = get_jwt_identity()
		user_status = User.query.filter_by(id=user).one_or_none()
		if user is not None:
					solicitud_edo= SolicitudEdo.query.filter_by(proveedor_id=user).first()
					#aca debo incluir una logica con el status de usuario
					if solicitud_edo is not None:
							return jsonify({
								"msg":"Ya tu tienes el estado de proveedor!"
							})
					else:
						#aca hay que agregar la fecha de cuando se pago
						solicitud_edo = SolicitudEdo(num_ref=body["num_ref"], proveedor_id=user )	
						try:
							db.session.add(solicitud_edo)
							db.session.commit()
							print(solicitud_edo)
							return jsonify(solicitud_edo.serialize()), 201
						except Exception as error:
							db.session.rollback()
							return jsonify(error.args), 500
		else:
				return jsonify({
								"msg": "Por favor entra en tu usuario!"
								}), 400
	else:
		return jsonify({
						"msg": "Algo paso, intentalo nuevamente [bad body format]"
						}), 400


@app.route('/evaluar', methods=['POST'])
# @app.route('/proveedores/<string:nature>/<int:name_id>', methods=['POST'])
@jwt_required()
def handle_evaluacion():
# def handle_add_favorite(nature, name_id):
	body=request.json
	body_service=body.get("nombre_tipo_servicio", None)
	body_proveedor=body.get("nombre_proveedor", None)
# creo que no hace falta, [update] lo que no es *****
#	body_nature=body.get("favorite_nature", None)

	if body_service is not  None:
		user = get_jwt_identity()
		cliente_asignado = User.query.filter_by(id=user).first()
		proveedor_asignado = User.query.filter_by(nombre=body_proveedor).first()
		servicio = TipoServicio.query.filter_by(nombre_tipo_servicio=body_service,  proveedor_id=proveedor_asignado.id ).first()
		orden_servicio= OrdenServicio.query.filter_by(detalle_servicio_id=servicio.id, cliente_id=cliente_asignado.id, proveedor_id=proveedor_asignado.id).first()
		print(orden_servicio)
		#falta hacer una logica con la orden de servicio
		if user is not None:
					evaluacion_proveedor= EvaluacionProveedor.query.filter_by(detalle_servicio_id=servicio.id, cliente_id=cliente_asignado.id, proveedor_id=proveedor_asignado.id).first()
					print(evaluacion_proveedor)
					if evaluacion_proveedor is not None:
							return jsonify({
								"msg":"La evaluacion por este servicio ya existe en tu perfil!"
							})
					else:
						evaluacion_proveedor = EvaluacionProveedor(detalle_servicio_id=servicio.id, proveedor_id=proveedor_asignado.id, cliente_id=cliente_asignado.id, resultado_evaluacion=body["resultado_evaluacion"], comentario=body["comentario"])	
						print(evaluacion_proveedor)
						try:
							db.session.add(evaluacion_proveedor)
							db.session.commit()
							return jsonify(evaluacion_proveedor.serialize()), 201
						except Exception as error:
							db.session.rollback()
							return jsonify(error.args), 500
		else:
				return jsonify({
								"msg": "Por favor entra en tu usuario!"
								}), 400
	else:
		return jsonify({
						"msg": "Algo paso, intentalo nuevamente [bad body format]"
						}), 400




# this only runs if `$ python src/main.py` is executed


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
