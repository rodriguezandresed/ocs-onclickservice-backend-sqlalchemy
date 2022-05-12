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
    login_status = db.Column(db.Boolean, nullable=False)
    fecha_registro = db.Column(db.Date, nullable=False)
    tipo_ususario = db.Column(db.String(250), nullable=False)
    social = db.Column(db.String(250), nullable=False)
    cliente_activo = db.Column(db.Boolean, nullable=False)
    proveedor_activo = db.Column(db.Boolean, nullable=False)
    imagen = db.Column(db.String(250), nullable=False)
    detalle = db.Column(db.String(250), nullable=False)
    fecha_activacion = db.Column(db.Date, nullable=False)



    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
			"id": self.id,
			"email": self.email,
			#do not serialize the password, it's a security breach
		}


# class Nature(db.Model):
#     # Here we define db.Columns for the table address.
#     # Notice that each db.db.Column is also a normal Python instance attribute.
#     id = db.db.db.Column(db.db.db.Integer, primary_key=True)
#     nature_name = db.db.db.Column(db.db.db.String(250))
#     nature_person = db.db.relationship('Person', backref="nature", uselist=True)
#     nature_planet = db.db.relationship('Planet', backref="nature", uselist=True)
#     nature_favorite = db.db.relationship('Favorite', backref="nature", uselist=True)

#     def __repr__(self):
#         return f'<Nature > f{self.nature_name}'

#     def serialize(self):
#         return {
# 			"natureName": self.natureName,
# 			#do not serialize the password, it's a security breach
# 		}



class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    login_status = db.Column(db.Boolean, nullable=False)
    fecha_registro = db.Column(db.Date, nullable=False)
    tipo_ususario = db.Column(db.String(250), nullable=False)
    social = db.Column(db.String(250), nullable=False)
    imagen = db.Column(db.String(250), nullable=False)
    detalle = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<Admin> f{self.id}'

    def serialize(self):
        return {
			"admin_name": self.nombre,
			"admin_email":self.email,
            "admin_social":self.social,
            "admin_id":self.id
			#do not serialize the password, it's a security breach
		}


class TipoServicio(db.Model):
    __tablename__ = 'tipo_servicio'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    proveedor_id= db.Column(db.Integer, db.ForeignKey('user.id') )
    status_active = db.Column(db.Boolean, nullable=False)
    nombre = db.Column(db.String(250), nullable=False)
    detalle = db.Column(db.String(250), nullable=False) 
    __table_args__ = (db.UniqueConstraint(
	"id","proveedor_id","detalle",
	name="debe_tener_una_sola_coincidencia"
    ),)


    def __repr__(self):
        return f'<Tipo de Servicio> f{self.id}'

    def serialize(self):
        return{
            "id":self.id,
            "proveedor_id":self.proveedor_id,
            "status_active":self.status_active,
            "nombre":self.nombre,
            "detalle":self.detalle,
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


class TipoSubServicio(db.Model):
    __tablename__ = 'tipo_sub_servicio'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    tipo_servicio_id= db.Column(db.Integer, db.ForeignKey('tipo_servicio.id') )
    status_activo = db.Column(db.Boolean, nullable=False)
    detalle = db.Column(db.String(250), nullable=False)
    nombre = db.Column(db.String(250), nullable=False)


    def __repr__(self):
        return f'<Tipo de SubServicio> f{self.id}'

    def serialize(self):
        return{
            "id":self.id,
            "tipo_servicio_id":self.tipo_servicio_id,
            "status_activo":self.status_activo,
            "nombre":self.nombre,
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


class DetalleServicio(db.Model):
    __tablename__ = 'detalle_servicio'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    tipo_servicio_id = db.Column(db.Integer, db.ForeignKey('tipo_sub_servicio.id') )
    evaluate_status = db.Column(db.Boolean, nullable=False)
    detalle = db.Column(db.String(250), nullable=False)
    nombre = db.Column(db.String(250), nullable=False)   


    def __repr__(self):
        return f'<Detalles del Servicio> f{self.id}'

    def serialize(self):
        return{
            "id":self.id,
            "nombre":self.nombre,
            "tipo_servicio_id":self.tipo_servicio_id,
            "evaluate_status":self.evaluate_status,
            "tipo_sub_servicio":self.tipo_sub_servicio,
            "detalle":self.detalle,
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

class EvaluacionProveedor(db.Model):
    __tablename__ = 'evaluacion_proveedor'
    # Here we define columns for the table person
    # Notice that each db.Column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.String(250), nullable=False)
    evaluate_status = db.Column(db.Boolean, nullable=False)
    detalle_servicio_id = db.Column(db.Integer, db.ForeignKey('detalle_servicio.id') )
    proveedor_id= db.Column(db.Integer, db.ForeignKey('user.id') )
    cliente_id= db.Column(db.Integer, db.ForeignKey('user.id') )
    resultado_evaluacion= db.Column(db.Float, nullable=False)


    def __repr__(self):
        return f'<Evaluacion del Proveedor> f{self.id}'

    def serialize(self):
        return{
            "id":self.id,
            "comentario":self.comentario,
            "evaluate_status":self.evaluate_status,
            "proveedor_id":self.proveedor_id,
            "cliente_id":self.cliente_id,
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
    status_orden_recibido = db.Column(db.Boolean, nullable=False)
    status_orden_cancelada = db.Column(db.Boolean, nullable=False)
    status_orden_aceptada = db.Column(db.Boolean, nullable=False)
    status_orden_progreso = db.Column(db.Boolean, nullable=False)
    detalle_servicio_id = db.Column(db.Integer, db.ForeignKey('detalle_servicio.id') )
    proveedor_id= db.Column(db.Integer, db.ForeignKey('user.id') ) 
    cliente_id= db.Column(db.Integer, db.ForeignKey('user.id') ) 



    def __repr__(self):
        return f'<Orden de Servicio> f{self.id}'

    def serialize(self):
        return{
            "id":self.id,
            "contador":self.contador,
            "precio_orden":self.precio_orden,
            "precio_total_orden":self.precio_total_orden,
            "status_orden_recibido":self.status_orden_recibido,
            "status_orden_aceptada":self.status_orden_aceptada,
            "status_orden_progreso":self.status_orden_progreso,
            "detalle_servicio_id":self.detalle_servicio_id,
            "proveedor_id":self.proveedor_id,
            "cliente_id":self.cliente_id,
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