from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
# connect to the database                  dbms      adapter   db_user password  url      port  db_name
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://feb_dev:123456@localhost:5432/feb_ecommerce"

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Model - Product
class Product(db.Model):
    # define tablename
    __tablename__ = "products"
    # define the primary key
    id = db.Column(db.Integer, primary_key=True)
    # more attributes
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

class ProductSchema(ma.Schema):
    class Meta:
        # fields
        fields = ("id", "name", "description", "price", "stock")

# to handle more than one product data
products_schema = ProductSchema(many=True)
# to handle a single product data
product_schema = ProductSchema()

# CLI Commands
@app.cli.command("create")
def create_db():
    db.create_all()
    print("Tables created")

@app.cli.command("seed")
def seed_db():
    # create a product instance / object
    product1 = Product(
        name="Product 1",
        description="Product 1 desc",
        price=4.75,
        stock=20
    )
    product2 = Product()
    product2.name = "Product 2"
    # product2.description = "Product 2 desc"
    product2.price = 159.99
    product2.stock = 150
    # add this to db session
    db.session.add(product1)
    db.session.add(product2)
    # commit
    db.session.commit()
    print("Tables seeded")

@app.cli.command("drop")
def drop_db():
    db.drop_all()
    print("Tables dropped")

products = [
    {
        'id': 0,
        'name': 'Product 0',
        'price': 110
    },
    {
        'id': 1,
        'name': 'Product 1',
        'price': 200
    },
    {
        'id': 2,
        'name': 'Product 2',
        'price': 330
    },
    {
        'id': 3,
        'name': 'Product 3',
        'price': 120
    }
]

@app.route("/")
def hello_word():
    return "<h1>Hello Hello World World</h1>"

@app.route("/another_route")
def another_route():
    return "This is another route, not the same as previous"

@app.route("/products")
def get_products():
    # products_list = Product.query.all() # SELECT * FROM products;
    stmt = db.select(Product) # SELECT * FROM products; [(1), (2), (3), (4)]
    products_list = db.session.scalars(stmt) # [1, 2, 3, 4]
    data = products_schema.dump(products_list) # JSON serializable object
    return data

@app.route("/products", methods=["POST"])
def create_product():
    product_fields = product_schema.load(request.get_json())
    new_product = Product(
        name=product_fields.get("name"),
        description=product_fields.get("description"),
        price=product_fields.get("price"),
        stock=product_fields.get("stock")
    )
    db.session.add(new_product)
    db.session.commit()
    return product_schema.dump(new_product), 201

# @app.route("/products/1", methods=["PUT"])
# def update_product1_put():
#     product = request.get_json() # only contain name and price
#     product['id'] = products[1]['id'] # copy id from original to new
#     products[1] = product # replace original with new
#     return jsonify(products[1])

@app.route("/products/<int:id>", methods=["PUT", "PATCH"])
def update_product(id):
    # find the product from the db to update
    stmt = db.select(Product).filter_by(id=id)
    product = db.session.scalar(stmt)
    # the data to be updated - received from body of put or patch request
    body_data = request.get_json()
    # updating the attributes
    if product:
        product.name = body_data.get('name') or product.name
        product.description = body_data.get('description') or product.description
        product.price = body_data.get('price') or product.price
        product.stock = body_data.get('stock') or product.stock
        # commit
        db.session.commit()
        return product_schema.dump(product)
    else:
        return jsonify(message=f"Product with id {id} doesn't exist"), 404


@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    stmt = db.select(Product).where(Product.id==id)
    product = db.session.scalar(stmt)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify(message=f"Product {product.name} deleted successfully")
    else:
        return jsonify(message=f"Product with id {id} doesn't exist"), 404


@app.route("/products/<int:id>")
def get_product(id):
    # product = Product.query.get(id) # SELECT * FROM products WHERE id=id(paramter)
    # product = db.session.get(Product, id)
    # OR to keep it consistent across all routes
    stmt = db.select(Product).filter_by(id=id)
    product = db.session.scalar(stmt)
    if(product):
        data = product_schema.dump(product)
        return data
    else:
        return jsonify(message="Product with that id doesn't exist"), 404

