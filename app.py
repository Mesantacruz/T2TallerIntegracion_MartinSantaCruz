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
  nombre = db_hamburguesa.Column(db_hamburguesa.String)
  precio = db_hamburguesa.Column(db_hamburguesa.Integer)
  descripcion = db_hamburguesa.Column(db_hamburguesa.String)
  imagen = db_hamburguesa.Column(db_hamburguesa.String)
  #ingredientes = db_hamburguesa.Column(db_hamburguesa.ARRAY(db_hamburguesa.String))

  def __init__(self, nombre, precio, descripcion, imagen, ingredientes):
    #self.id = int()
    self.nombre = nombre
    self.precio = precio
    self.descripcion = descripcion
    self.imagen = imagen
    self.ingredientes = ingredientes

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
  try:
    nombre = str(request.json['nombre'])
    precio = request.json['precio']
    descripcion = str(request.json['descripcion'])
    imagen = str(request.json['imagen'])
  except (ValueError, KeyError, TypeError):
    return "input invalido", "400 input invalido"
  lista = request.json
  if len(lista) != 4:
    return "input invalido", "400 input invalido"

  try:
    precio = int(precio)
  except (ValueError):
    return "input invalido", "400 input invalido"

  nueva_hamburguesa = Hamburguesa(nombre, precio, descripcion, imagen, [])

  db_hamburguesa.session.add(nueva_hamburguesa)
  db_hamburguesa.session.commit()

  db_hamburguesa.session.refresh(nueva_hamburguesa)

  string = "{\n  \"id\": "+ str(nueva_hamburguesa.id)+",\n  \"nombre\": \""+nombre+"\",\n  \"precio\": "+str(precio)+",\n  \"descripcion\": \""+descripcion+"\",\n  \"imagen\": \""+imagen+"\"\n  \"ingredientes\": [\n    {"

  all_mezclas = Mezcla.query.all()
  for i in all_mezclas:
    if int(i.id_hamburguesa) == int(nueva_hamburguesa.id):
      string += "\n      \"path\": \"https://api-santacruz17.herokuapp.com/"+str(i.id_ingrediente)+"\""   #https://

  string += "\n    }\n  ]\n}"

  return hamburguesa_schema.jsonify(nueva_hamburguesa), "201 hamburguesa creada"

# Get All Products
@app.route('/hamburguesa', methods=['GET'])
def get_hamburguesas():
  all_hamburguesas = Hamburguesa.query.all()
  result = hamburguesas_schema.dump(all_hamburguesas)
  lista_final = []
  print(result)
  #if not result:
  #  return "[\n]", "200 resultados obtenidos"
  string = "[\n"
  for k in result:
    string += "  {  \n    \"id\": " + str(k['id']) + ",\n    \"nombre\": \"" + k['nombre'] + "\",\n    \"precio\": " + str(
      k['precio']) + ",\n    \"descripcion\": \"" + k['descripcion'] + "\",\n    \"imagen\": \"" + k['imagen'] + "\"\n    \"ingredientes\": [\n"

    k["ingredientes"] = []
    all_mezclas = Mezcla.query.all()
    for i in all_mezclas:
      if int(i.id_hamburguesa) == int(k['id']):
        estring = "https://api-santacruz17.herokuapp.com/ingrediente/" + str(i.id_ingrediente)
        k["ingredientes"].append({"path": estring})
        string += "      {\n        \"path\": \"https://api-santacruz17.herokuapp.com/ingrediente/" + str(i.id_ingrediente) + "\"\n      },\n" # https://

    if string[-2] == "[":
      string += "    ]\n  },\n"
    else:
      string = string[:-2] + "\n    ]\n  },\n"
    lista_final.append(k)

  string = string[:-2] + "\n]"

  return jsonify(result), "200 resultados obtenidos"

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

  hamburguesa.ingredientes = []

  all_mezclas = Mezcla.query.all()
  for i in all_mezclas:
    if int(i.id_hamburguesa) == int(id):
      estring = "https://api-santacruz17.herokuapp.com/ingrediente/" + str(i.id_ingrediente)
      hamburguesa.ingredientes.append({"path": estring})
      string += "    {\n      \"path\": \"https://api-santacruz17.herokuapp.com/ingrediente/" + str(i.id_ingrediente) + "\"\n    },\n" # https://

  if string[-2] == "[":
    string += "  ]\n}"
  else:
    string = string[:-2] + "\n  ]\n}"

  return hamburguesa_schema.jsonify(hamburguesa), "200 operacion exitosa"

# Update a Product
@app.route('/hamburguesa/<id>', methods=['PATCH'])
def update_hamburguesa(id):
  cant = 0
  hamburguesa = Hamburguesa.query.get(id)
  if not hamburguesa:
    return "Hamburguesa inexistente", "400 Hamburguesa inexistente"
  try:
    nombre = str(request.json['nombre'])
    hamburguesa.nombre = nombre
    cant += 1
  except (ValueError, KeyError, TypeError):
    pass
  try:
    precio = request.json['precio']
    cant += 1
  except (ValueError, KeyError, TypeError):
    pass
  try:
    descripcion = str(request.json['descripcion'])
    hamburguesa.descripcion = descripcion
    cant += 1
  except (ValueError, KeyError, TypeError):
    pass
  try:
    imagen = str(request.json['imagen'])
    hamburguesa.imagen = imagen
    cant += 1
  except (ValueError, KeyError, TypeError):
    pass


  try:
    precio = int(precio)
  except (ValueError):
    return "Parametros invalidos", "400 Parametros invalidos"
  hamburguesa.precio = precio

  if cant == 0:
    return "Parametros invalidos", "400 Parametros invalidos"
  lista = request.json
  if len(lista) != cant:
    return "Parametros invalido", "400 Parametros invalido"

  db_hamburguesa.session.commit()

  string = "{\n  \"id\": " + str(id) + ",\n  \"nombre\": \"" + hamburguesa.nombre + "\",\n  \"precio\": " + str(
    hamburguesa.precio) + ",\n  \"descripcion\": \"" + hamburguesa.descripcion + "\",\n  \"imagen\": \"" + hamburguesa.imagen + "\"\n  \"ingredientes\": [\n"

  hamburguesa.ingredientes = []

  all_mezclas = Mezcla.query.all()
  for i in all_mezclas:
    if int(i.id_hamburguesa) == int(id):
      estring = "https://api-santacruz17.herokuapp.com/ingrediente/" + str(i.id_ingrediente)
      hamburguesa.ingredientes.append({"path": estring})
      string += "    {\n      \"path\": \"https://api-santacruz17.herokuapp.com/ingrediente/" + str(i.id_ingrediente) + "\"\n    },\n" # https://

  if string[-2] == "[":
    string += "  ]\n}"
  else:
    string = string[:-2] + "\n  ]\n}"

  return hamburguesa_schema.jsonify(hamburguesa), "200 operacion exitosa"

# Delete Product
@app.route('/hamburguesa/<id>', methods=['DELETE'])
def delete_hamburguesa(id):
  hamburguesa = Hamburguesa.query.get(id)
  if not hamburguesa:
    return "hamburguesa inexistente", "404 hamburguesa inexistente"

  mezclas = []

  all_mezclas = Mezcla.query.all()
  for i in all_mezclas:
    if int(i.id_hamburguesa) == int(id):
      mezclas.append(i)


  if mezclas:
    for i in mezclas:
      db_mezcla.session.delete(i)
      db_mezcla.session.commit()

  db_hamburguesa.session.delete(hamburguesa)
  db_hamburguesa.session.commit()


  return "hamburguesa eliminada", "200 hamburguesa eliminada"







# Product Class/Model
class Ingrediente(db_ingredientes.Model):
  id = db_ingredientes.Column(db_ingredientes.Integer, primary_key=True)
  nombre = db_ingredientes.Column(db_ingredientes.String)
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
  try:
    nombre = str(request.json['nombre'])
    descripcion = str(request.json['descripcion'])
  except (ValueError, KeyError, TypeError):
    return "input invalido", "400 input invalido"
  lista = request.json
  if len(lista) > 2:
    return "input invalido", "400 input invalido"

  nuevo_ingrediente = Ingrediente(nombre, descripcion)

  db_ingredientes.session.add(nuevo_ingrediente)
  db_ingredientes.session.commit()

  db_ingredientes.session.refresh(nuevo_ingrediente)

  return ingrediente_schema.jsonify(nuevo_ingrediente), "201 ingrediente creado"

# Get All Products
@app.route('/ingrediente', methods=['GET'])
def get_ingredientes():
  all_ingredientes = Ingrediente.query.all()
  result = ingredientes_schema.dump(all_ingredientes)
  string = "["
  for i in result:
    string += "\n  {"
    string += "\n    \"id\": "+str(i['id'])+",\n    \"nombre\": \""+str(i['nombre'])+"\",\n    \"descripcion\": \""+str(i['descripcion']) + "\""
    string += "\n  }"
  string += "\n]"
  return jsonify(result), "200 resultados obtenidos"

# Get Single Products
@app.route('/ingrediente/<id>', methods=['GET'])
def get_ingrediente(id):
  ingrediente = Ingrediente.query.get(id)
  if not id.isdigit():
    return "id invalido", "400 id invalido"
  if not ingrediente:
    return "ingrediente inexistente", "404 ingrediente inexistente"
  string = "{\n  \"id\": " + str(id) + ",\n  \"nombre\": \"" + ingrediente.nombre + "\",\n  \"descripcion\": \"" + ingrediente.descripcion + "\"\n}"
  return ingrediente_schema.jsonify(ingrediente), "200 operacion exitosa"

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
