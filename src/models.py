from collections import UserList
from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class TipoUser(str, enum.Enum):
    General = "General"
    Admin = "Admin"
    Proveedor = "Proveedor"

class TiposServicio(str, enum.Enum):
    General = "General"
    Plomeria = "Plomeria"
    Carpinteria = "Carpinteria"
    Computacion = "Computacion"
    Albanileria = "Albanileria"
    Cocina = "Cocina"
    Limpieza = "Limpieza"
    Acondicionado = "Aire Acondicionado"
    Fumigacion = "Fumigacion"


class User(db.Model):
    __tablename__ = 'user'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    login_status = db.Column(db.Boolean)
    fecha_registro = db.Column(db.Date, nullable=False)
    tipo_usuario = db.Column(db.Enum(TipoUser), nullable=False)
    social = db.Column(db.String(250))
    cliente_activo = db.Column(db.Boolean)
    proveedor_activo = db.Column(db.Boolean)
    imagen = db.Column(db.String(250))
    detalle = db.Column(db.String(250))
    fecha_activacion = db.Column(db.Date)
    direccion = db.Column(db.String(250))
    telefono = db.Column(db.String(250))
    servicios = db.relationship('TipoServicio', backref='user', uselist=True)
    __table_args__ = (db.UniqueConstraint(
	"id","email","social","telefono",
	name="debe_tener_una_sola_coincidencia"
    ),)

    def __repr__(self):
        return '<User %r>' % self.nombre

    def serialize(self):
        return {
			"id": self.id,
            "nombre": self.nombre,
			"email": self.email,
            "fecha_registro":self.fecha_registro,
            "tipo_usuario":self.tipo_usuario,
            "cliente_activo":self.cliente_activo,
            "proveedor_activo":self.proveedor_activo,           
            "detalle":self.detalle,
            "fecha_activacion":self.fecha_activacion,
            "imagen":self.imagen,  
            "social":self.social,
            "direccion":self.direccion,
            "telefono":self.telefono,
            "servicio":[test.serialize() for test in self.servicios ]              
			#do not serialize the password, it's a security breach
		}


    def simplify(self):
        return {
			"id": self.id,
            "nombre": self.nombre,
			"email": self.email,
            "fecha_registro":self.fecha_registro,
            "tipo_usuario":self.tipo_usuario,
            "cliente_activo":self.cliente_activo,
            "proveedor_activo":self.proveedor_activo,           
            "detalle":self.detalle,
            "fecha_activacion":self.fecha_activacion,
            "imagen":self.imagen,  
            "social":self.social,
            "direccion":self.direccion,
            "telefono":self.telefono,
            }


class TipoServicio(db.Model):
    __tablename__ = 'tipo_servicio'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    status_active = db.Column(db.Boolean)
    nombre_tipo_servicio = db.Column(db.Enum(TiposServicio), nullable=False)
    nombre_tipo_sub_servicio = db.Column(db.String(250), nullable=False)
    detalle_tipo_servicio = db.Column(db.String(250), nullable=False)
    #Defining Foreign Keys
    proveedor_id= db.Column(db.Integer, db.ForeignKey('user.id') )


    __table_args__ = (db.UniqueConstraint(
	"id","proveedor_id","nombre_tipo_servicio","nombre_tipo_sub_servicio","detalle_tipo_servicio","status_active",
	name="debe_tener_una_sola_coincidencia"
    ),)


    def __repr__(self):
        return f'<Tipo de Servicio> {self.nombre_tipo_servicio}'

    def serialize(self):
        user =User.query.filter_by(id=self.proveedor_id).first()
        return{
            "id":self.id,
            "proveedor_id":self.proveedor_id,
            "status_active":self.status_active,
            "nombre":self.nombre_tipo_servicio,
            "sub_servicio":self.nombre_tipo_sub_servicio,
            "detalle":self.detalle_tipo_servicio,
            "nombre_tipo_servicio":self.nombre_tipo_servicio,
            "proveedor":user.simplify(),
        }

    def __init__(self, *args, **kwargs):
        """
            "name":"andres",
            "lastname":"rodriguez"


        """
      

        for (key, value) in kwargs.items():
            if hasattr(self, key):
                attr_type = getattr(self.__class__, key).type

                try:
                    attr_type.python_type(value)
                    setattr(self, key, value)
                except Exception as error:
                    print(f"ignota los demas valores: {error.args}")

    @classmethod
    def create(cls, data):
        # creamos instancia
        instance = cls(**data)
        if (not isinstance(instance, cls)):
            print("These aren't the droids you're looking for")
            return None
        db.session.add(instance)
        try:
            db.session.commit()
            print(f"Created: {instance.name}")
            return instance
        except Exception as error:
            db.session.rollback()
            print(error.args)




class EvaluacionProveedor(db.Model):
    __tablename__ = 'evaluacion_proveedor'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.String(250))
    evaluate_status = db.Column(db.Boolean)
    resultado_evaluacion= db.Column(db.Float, nullable=False)
    #Defining Foreign Keys
    detalle_servicio_id = db.Column(db.Integer, db.ForeignKey('tipo_servicio.id') )
    cliente_evaluador_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    proveedor_evaluado_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    #Defining Relationships
    cliente_evaluador = db.relationship("User", foreign_keys=[cliente_evaluador_id])
    proveedor_evaluado = db.relationship("User", foreign_keys=[proveedor_evaluado_id])
    detalle_servicio = db.relationship("TipoServicio", foreign_keys=[detalle_servicio_id])



    def __repr__(self):
        return f'<Evaluacion del Proveedor> f{self.id}'

    def serialize(self):
        return{
            "id":self.id,
            "comentario":self.comentario,
            "evaluate_status":self.evaluate_status,
            "detalle_servicio":self.detalle_servicio.serialize(),
            "proveedor_id":self.proveedor_evaluado.serialize(),
            "cliente_id":self.cliente_evaluador.serialize(),
            "resultado_evaluacion":self.resultado_evaluacion,
        }

    def __init__(self, *args, **kwargs):
        """
            "name":"andres",
            "lastname":"rodriguez"


        """
      

        for (key, value) in kwargs.items():
            if hasattr(self, key):
                attr_type = getattr(self.__class__, key).type

                try:
                    attr_type.python_type(value)
                    setattr(self, key, value)
                except Exception as error:
                    print(f"Ignore the rest: {error.args}")

class OrdenServicio(db.Model):
    __tablename__ = 'orden_servicio'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    contador = db.Column(db.Integer)
    precio_orden = db.Column(db.Float)
    precio_total_orden = db.Column(db.Float)
    status_orden_recibida = db.Column(db.Boolean)
    status_orden_cancelada = db.Column(db.Boolean)
    status_orden_aceptada = db.Column(db.Boolean)
    status_orden_progreso = db.Column(db.Boolean) 
    #Defining Foreign Keys
    detalle_servicio_id = db.Column(db.Integer, db.ForeignKey('tipo_servicio.id') )
    cliente_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    proveedor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    #Defining Relationships
    cliente = db.relationship("User", foreign_keys=[cliente_id])
    proveedor = db.relationship("User", foreign_keys=[proveedor_id])
    detalle_servicio = db.relationship("TipoServicio", foreign_keys=[detalle_servicio_id])

    def __repr__(self):
        return f'<Orden de Servicio> f{self.id}'

    def serialize(self):
        return{
            "id":self.id,
            "contador":self.contador,
            "precio_orden":self.precio_orden,
            "precio_total_orden":self.precio_total_orden,
            "status_orden_recibido":self.status_orden_recibida,
            "status_orden_aceptada":self.status_orden_aceptada,
            "status_orden_progreso":self.status_orden_progreso,
            "detalle_servicio_id":self.detalle_servicio_id,
            "proveedor_id":self.proveedor_id,
            "cliente_id":self.cliente_id,
            "orden_detalle_servicio":self.detalle_servicio.serialize(),
        }

    def __init__(self, *args, **kwargs):
        """
            "name":"andres",
            "lastname":"rodriguez"


        """
      

        for (key, value) in kwargs.items():
            if hasattr(self, key):
                attr_type = getattr(self.__class__, key).type

                try:
                    attr_type.python_type(value)
                    setattr(self, key, value)
                except Exception as error:
                    print(f"Ignore the rest: {error.args}")


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

class SolicitudEdo(db.Model):
    __tablename__ = 'solicitud_edo'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    status_active = db.Column(db.Boolean)
    num_ref = db.Column(db.String(250), nullable=False)
    comentarios = db.Column(db.String(250))
    #Defining Foreign Keys
    proveedor_id= db.Column(db.Integer, db.ForeignKey('user.id') )
    #Defining Relationships
    proveedor = db.relationship("User", foreign_keys=[proveedor_id])

    __table_args__ = (db.UniqueConstraint(
	"id","proveedor_id","num_ref",
	name="debe_tener_una_sola_coincidencia"
    ),)


    def __repr__(self):
        return f'<Tipo de Servicio> {self.nombre_tipo_servicio}'

    def serialize(self):
        return{
            "id":self.id,
            "num_ref":self.num_ref,
            "proveedor":self.proveedor.serialize(),
            "status_active":self.status_active,
        }

    def __init__(self, *args, **kwargs):
        """
            "name":"andres",
            "lastname":"rodriguez"


        """
      

        for (key, value) in kwargs.items():
            if hasattr(self, key):
                attr_type = getattr(self.__class__, key).type

                try:
                    attr_type.python_type(value)
                    setattr(self, key, value)
                except Exception as error:
                    print(f"ignota los demas valores: {error.args}")



    