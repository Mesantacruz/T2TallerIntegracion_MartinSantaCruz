from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db_hamburguesa = SQLAlchemy(app)
db_ingredientes = SQLAlchemy(app)
db_mezcla = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# Product Class/Model
class Hamburguesa(db_hamburguesa.Model):
  id = db_hamburguesa.Column(db_hamburguesa.Integer, primary_key=True)
  nombre = db_hamburguesa.Column(db_hamburguesa.String, unique=True)
  precio = db_hamburguesa.Column(db_hamburguesa.Integer)
  descripcion = db_hamburguesa.Column(db_hamburguesa.String)
  imagen = db_hamburguesa.Column(db_hamburguesa.String)
  #ingredientes = db_hamburguesa.Column(db_hamburguesa.ARRAY(db_hamburguesa.String))

  def __init__(self, nombre, precio, descripcion, imagen):
    self.nombre = nombre
    self.precio = precio
    self.descripcion = descripcion
    self.imagen = imagen
    #self.ingredientes = list()

# Product Schema
class HamburguesaSchema(ma.Schema):
  class Meta:
    fields = ('id', 'nombre', 'precio', 'descripcion', 'imagen', 'ingredientes')

# Init schema
hamburguesa_schema = HamburguesaSchema()
hamburguesas_schema = HamburguesaSchema(many=True)

# Create a Product
@app.route('/hamburguesa', methods=['POST'])
def add_hamburguesa():
  nombre = request.json['nombre']
  precio = request.json['precio']
  descripcion = request.json['descripcion']
  imagen = request.json['imagen']

  nueva_hamburguesa = Hamburguesa(nombre, precio, descripcion, imagen)

  db_hamburguesa.session.add(nueva_hamburguesa)
  db_hamburguesa.session.commit()

  db_hamburguesa.session.refresh(nueva_hamburguesa)

  string = "{\n  \"id\": "+ str(nueva_hamburguesa.id)+",\n  \"nombre\": \""+nombre+"\",\n  \"precio\": "+str(precio)+",\n  \"descripcion\": \""+descripcion+"\",\n  \"imagen\": \""+imagen+"\"\n  \"ingredientes\": [\n    {"

  all_mezclas = Mezcla.query.all()
  for i in all_mezclas:
    if int(i.id_hamburguesa) == int(nueva_hamburguesa.id):
      string += "\n      \"path\": localhost:5000/ingrediente/"+str(i.id_ingrediente)   #https://

  string += "\n    }\n  ]\n}"

  return string, "201 hamburguesa creada"
  #falta hacer el 400 input invalido

# Get All Products
@app.route('/hamburguesa', methods=['GET'])
def get_hamburguesas():
  all_hamburguesas = Hamburguesa.query.all()
  result = hamburguesas_schema.dump(all_hamburguesas)
  if not result:
    return "[\n]", "200 resultados obtenidos"
  string = "[\n"
  for k in result:
    string += "  {  \n    \"id\": " + str(k['id']) + ",\n    \"nombre\": \"" + k['nombre'] + "\",\n    \"precio\": " + str(
      k['precio']) + ",\n    \"descripcion\": \"" + k['descripcion'] + "\",\n    \"imagen\": \"" + k['imagen'] + "\"\n    \"ingredientes\": [\n"

    all_mezclas = Mezcla.query.all()
    for i in all_mezclas:
      if int(i.id_hamburguesa) == int(k['id']):
        string += "      {\n        \"path\": localhost:5000/ingrediente/" + str(i.id_ingrediente) + "\n      },\n" # https://

    if string[-2] == "[":
      string += "    ]\n  },\n"
    else:
      string = string[:-2] + "\n    ]\n  },\n"

  string = string[:-2] + "\n]"
  return string, "200 resultados obtenidos"

# Get Single Products
@app.route('/hamburguesa/<id>', methods=['GET'])
def get_hamburguesa(id):
  hamburguesa = Hamburguesa.query.get(id)
  if not id.isdigit():
    return "id invalido", "400 id invalido"
  if not hamburguesa:
    return "hamburguesa inexistente", "404 hamburguesa inexistente"

  string = "{\n  \"id\": " + str(id) + ",\n  \"nombre\": \"" + hamburguesa.nombre + "\",\n  \"precio\": " + str(
    hamburguesa.precio) + ",\n  \"descripcion\": \"" + hamburguesa.descripcion + "\",\n  \"imagen\": \"" + hamburguesa.imagen + "\"\n  \"ingredientes\": [\n"

  all_mezclas = Mezcla.query.all()
  for i in all_mezclas:
    if int(i.id_hamburguesa) == int(id):
      string += "    {\n      \"path\": localhost:5000/ingrediente/" + str(i.id_ingrediente) + "\n    },\n" # https://

  if string[-2] == "[":
    string += "  ]\n}"
  else:
    string = string[:-2] + "\n  ]\n}"

  return string, "200 operacion exitosa"

# Update a Product
@app.route('/hamburguesa/<id>', methods=['PATCH'])
def update_hamburguesa(id):
  hamburguesa = Hamburguesa.query.get(id)

  nombre = request.json['nombre']
  precio = request.json['precio']
  descripcion = request.json['descripcion']
  imagen = request.json['imagen']

  hamburguesa.nombre = nombre
  hamburguesa.precio = precio
  hamburguesa.descripcion = descripcion
  hamburguesa.imagen = imagen

  db_hamburguesa.session.commit()

  return hamburguesa_schema.jsonify(hamburguesa)

# Delete Product
@app.route('/hamburguesa/<id>', methods=['DELETE'])
def delete_hamburguesa(id):
  hamburguesa = Hamburguesa.query.get(id)
  if not hamburguesa:
    return "hamburguesa inexistente", "404 hamburguesa inexistente"
  db_hamburguesa.session.delete(hamburguesa)
  db_hamburguesa.session.commit()


  return hamburguesa_schema.jsonify(hamburguesa), "200 hamburguesa eliminada"







# Product Class/Model
class Ingrediente(db_ingredientes.Model):
  id = db_ingredientes.Column(db_ingredientes.Integer, primary_key=True)
  nombre = db_ingredientes.Column(db_ingredientes.String, unique=True)
  descripcion = db_ingredientes.Column(db_ingredientes.String)

  def __init__(self, nombre, descripcion):
    self.nombre = nombre
    self.descripcion = descripcion

# Product Schema
class IngredienteSchema(ma.Schema):
  class Meta:
    fields = ('id', 'nombre', 'descripcion')

# Init schema
ingrediente_schema = HamburguesaSchema()
ingredientes_schema = HamburguesaSchema(many=True)

# Create a Product
@app.route('/ingrediente', methods=['POST'])
def add_ingrediente():
  nombre = request.json['nombre']
  descripcion = request.json['descripcion']

  nuevo_ingrediente = Ingrediente(nombre, descripcion)

  db_ingredientes.session.add(nuevo_ingrediente)
  db_ingredientes.session.commit()

  db_ingredientes.session.refresh(nuevo_ingrediente)

  return "{\n  \"id\": "+ str(nuevo_ingrediente.id)+",\n  \"nombre\": "+nombre+",\n  \"descripcion\": "+descripcion+"\n}", "201 ingrediente creado"

# Get All Products
@app.route('/ingrediente', methods=['GET'])
def get_ingredientes():
  all_ingredientes = Ingrediente.query.all()
  result = ingredientes_schema.dump(all_ingredientes)
  string = "["
  for i in result:
    string += "\n  {"
    string += "\n    \"id\": "+str(i['id'])+",\n    \"nombre\": "+str(i['nombre'])+",\n    \"descripcion\": "+str(i['descripcion'])
    string += "\n  }"
  string += "\n]"
  return string, "200 resultados obtenidos"

# Get Single Products
@app.route('/ingrediente/<id>', methods=['GET'])
def get_ingrediente(id):
  ingrediente = Ingrediente.query.get(id)
  if not id.isdigit():
    return "id invalido", "400 id invalido"
  if not ingrediente:
    return "ingrediente inexistente", "404 ingrediente inexistente"
  string = "{\n  \"id\": " + id + ",\n  \"nombre\": " + ingrediente.nombre + ",\n  \"descrpcion\": " + ingrediente.descripcion + "\n}"
  return string, "200 operacion exitosa"

# Delete Product
@app.route('/ingrediente/<id>', methods=['DELETE'])
def delete_ingrediente(id):
  ingrediente = Ingrediente.query.get(id)
  if not id.isdigit():
    return "ingrediente inexistente", "404 ingrediente inexistente"
  if not ingrediente:
    return "ingrediente inexistente", "404 ingrediente inexistente"

  all_mezclas = Mezcla.query.all()
  for i in all_mezclas:
    if int(i.id_ingrediente) == int(id):
      return "Ingrediente no se puede borrar, se encuentra presente en una hamburguesa", "409 Ingrediente no se puede borrar, se encuentra presente en una hamburguesa"

  db_ingredientes.session.delete(ingrediente)
  db_ingredientes.session.commit()

  return "ingrediente eliminado", "200 ingrediente eliminado"






class Mezcla(db_mezcla.Model):
  id = db_mezcla.Column(db_mezcla.Integer, primary_key=True)
  id_hamburguesa = db_mezcla.Column(db_mezcla.Integer)
  id_ingrediente = db_mezcla.Column(db_mezcla.String)

  def __init__(self, id_hamburguesa, id_ingrediente):
    self.id_hamburguesa = id_hamburguesa
    self.id_ingrediente = id_ingrediente

# Product Schema
class MezclaSchema(ma.Schema):
  class Meta:
    fields = ('id', 'id_hamburguesa', 'id_ingrediente')

# Init schema
mezcla_schema = HamburguesaSchema()
mezclas_schema = HamburguesaSchema(many=True)

# Create Relacion
@app.route('/hamburguesa/<id_hamburguesa>/ingrediente/<id_ingrediente>', methods=['PUT'])
def add_relacion(id_hamburguesa, id_ingrediente):
  hamburguesa = Hamburguesa.query.get(id_hamburguesa)
  if not id_hamburguesa.isdigit():
    return "Id de hamburguesa invalido", "400 Id de hamburguesa invalido"
  if not hamburguesa:
    return "Id de hamburguesa invalido", "400 Id de hamburguesa invalido"
  ingrediente = Ingrediente.query.get(id_ingrediente)
  if not id_ingrediente.isdigit():
    return "Ingrediente inexistente", "404 Ingrediente inexistente"
  if not ingrediente:
    return "Ingrediente inexistente", "404 Ingrediente inexistente"

  all_mezclas = Mezcla.query.all()
  for i in all_mezclas:
    if int(i.id_hamburguesa) == int(id_hamburguesa) and int(i.id_ingrediente) == int(id_ingrediente):
      return "Ingrediente agregado", "201 Ingrediente agregado"

  mezcla = Mezcla(id_hamburguesa, id_ingrediente)

  db_mezcla.session.add(mezcla)
  db_mezcla.session.commit()

  return "Ingrediente agregado", "201 Ingrediente agregado"

# Get All Mezclas
@app.route('/mezclas', methods=['GET'])
def get_mezclas():
  all_mezclas = Mezcla.query.all()
  print(all_mezclas)
  for i in all_mezclas:
    print(i.id_hamburguesa, i.id_ingrediente)
  result = mezclas_schema.dump(all_mezclas)
  print(result)
  return jsonify(result), "200 resultados obtenidos"

# Delete Mezcla
@app.route('/hamburguesa/<id_hamburguesa>/ingrediente/<id_ingrediente>', methods=['DELETE'])
def delete_mezcla(id_hamburguesa, id_ingrediente):
  hamburguesa = Hamburguesa.query.get(id_hamburguesa)
  if not id_hamburguesa.isdigit():
    return "Id de hamburguesa invalido", "400 Id de hamburguesa invalido"
  if not hamburguesa:
    return "Id de hamburguesa invalido", "400 Id de hamburguesa invalido"
  ingrediente = Ingrediente.query.get(id_ingrediente)
  if not id_ingrediente.isdigit():
    return "Ingrediente inexistente en la hamburguesa", "404 Ingrediente inexistente en la hamburguesa"
  if not ingrediente:
    return "Ingrediente inexistente en la hamburguesa", "404 Ingrediente inexistente en la hamburguesa"

  mezcla = None

  all_mezclas = Mezcla.query.all()
  for i in all_mezclas:
    if int(i.id_hamburguesa) == int(id_hamburguesa) and int(i.id_ingrediente) == int(id_ingrediente):
      mezcla = i

  if not mezcla:
    return "Ingrediente inexistente en la hamburguesa", "404 Ingrediente inexistente en la hamburguesa"

  db_mezcla.session.delete(mezcla)
  db_mezcla.session.commit()

  return "ingrediente retirado", "200 ingrediente retirado"


# Run Server
if __name__ == '__main__':
  app.run(debug=True)