from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



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
    tipo_usuario = db.Column(db.String(250), nullable=False)
    social = db.Column(db.String(250))
    cliente_activo = db.Column(db.Boolean)
    proveedor_activo = db.Column(db.Boolean)
    imagen = db.Column(db.String(250))
    detalle = db.Column(db.String(250))
    fecha_activacion = db.Column(db.Date)
    direccion = db.Column(db.String(250))
    telefono = db.Column(db.String(250))


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
			#do not serialize the password, it's a security breach
		}




class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    fecha_registro = db.Column(db.Date, nullable=False)
    tipo_ususario = db.Column(db.String(250))
    detalle = db.Column(db.String(250))
    
    def __repr__(self):
        return f'<Admin> f{self.nombre}'

    def serialize(self):
        return {
			"admin_name": self.nombre,
			"admin_email":self.email,
            "admin_id":self.id,
            "admin_detalle":self.detalle,
			#do not serialize the password, it's a security breach
		}


class TipoServicio(db.Model):
    __tablename__ = 'tipo_servicio'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    proveedor_id= db.Column(db.Integer, db.ForeignKey('user.id') )
    status_active = db.Column(db.Boolean, nullable=False)
    nombre_tipo_servicio = db.Column(db.String(250), nullable=False)
    nombre_tipo_sub_servicio = db.Column(db.String(250), nullable=False)
    detalle_tipo_servicio = db.Column(db.String(250), nullable=False)
    user_proveedor = db.relationship('User', backref="tipo_servicio", uselist=False)  
    __table_args__ = (db.UniqueConstraint(
	"id","proveedor_id","nombre_tipo_servicio","nombre_tipo_sub_servicio","detalle_tipo_servicio","status_active",
	name="debe_tener_una_sola_coincidencia"
    ),)


    def __repr__(self):
        return f'<Tipo de Servicio> f{self.nombre_tipo_servicio}'

    def serialize(self):
        return{
            "id":self.id,
            "proveedor_id":self.proveedor_id,
            "status_active":self.status_active,
            "nombre":self.nombre_tipo_servicio,
            "sub_servicio":self.nombre_tipo_sub_servicio,
            "detalle":self.detalle_tipo_servicio,
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
    comentario = db.Column(db.String(250), nullable=False)
    evaluate_status = db.Column(db.Boolean, nullable=False)
    detalle_servicio_id = db.Column(db.Integer, db.ForeignKey('tipo_servicio.id') )
    user_id= db.Column(db.Integer, db.ForeignKey('user.id') )
    resultado_evaluacion= db.Column(db.Float, nullable=False)
    cliente_evaluador = db.relationship('User', backref="cliente_evaluador", uselist=False) 
    proveedor_evaluado = db.relationship('User', backref="proveedor_evaluado", uselist=False)   
    detalle_servicio_evaluado = db.relationship('TipoServicio', backref="detalle_servicio_evaluado", uselist=False)


    def __repr__(self):
        return f'<Evaluacion del Proveedor> f{self.id}'

    def serialize(self):
        return{
            "id":self.id,
            "comentario":self.comentario,
            "evaluate_status":self.evaluate_status,
            "detalle_servicio_evaluado":self.detalle_servicio_evaluado,
            "proveedor_id":self.proveedor_evaluado,
            "cliente_id":self.cliente_evaluador,
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
    contador = db.Column(db.Integer, nullable=False)
    precio_orden = db.Column(db.Float, nullable=False)
    precio_total_orden = db.Column(db.Float, nullable=False)
    status_orden_recibida = db.Column(db.Boolean, nullable=False)
    status_orden_cancelada = db.Column(db.Boolean, nullable=False)
    status_orden_aceptada = db.Column(db.Boolean, nullable=False)
    status_orden_progreso = db.Column(db.Boolean, nullable=False) 
    detalle_servicio_id = db.Column(db.Integer, db.ForeignKey('tipo_servicio.id') )
    user_id= db.Column(db.Integer, db.ForeignKey('user.id') ) 
    orden_cliente = db.relationship('User', backref="orden_cliente", uselist=False)
    orden_proveedor = db.relationship('User', backref="orden_proveedor", uselist=False) 
    orden_detalle_servicio = db.relationship('TipoServicio', backref="orden_detalle_servicio", uselist=False)


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
            "proveedor_id":self.orden_proveedor,
            "cliente_id":self.orden_cliente,
            "orden_detalle_servicio":self.orden_detalle_servicio,
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


    @classmethod
    def create(cls, data):
        # creamos instancia
        instance = cls(**data)
        if (not isinstance(instance, cls)):
            print("We failed")
            return None
        db.session.add(instance)
        try:
            db.session.commit()
            print(f"Created: {instance.name}")
            return instance
        except Exception as error:
            db.session.rollback()
            print(error.args)