from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import psycopg2
import os

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URI')
POSTGRES_URI = os.environ.get('POSTGRES_URI')


def create_table():
    try:
        postgres_conn = psycopg2.connect(POSTGRES_URI)
        postgres_cursor = postgres_conn.cursor()
        postgres_cursor.execute("""
            CREATE TABLE IF NOT EXISTS worker (
                id SERIAL PRIMARY KEY,
                firstname VARCHAR(255) NOT NULL,
                lastname VARCHAR(255) NOT NULL,
                post VARCHAR(255) NOT NULL
            );
        """)
        postgres_conn.commit()
        postgres_cursor.close()
    except Exception as e:
        print(f"Error creating workers table: {str(e)}")


@app.route('/', methods=['GET'])
def index():
    return 'Shop'


@app.route('/product', methods=['POST'])
def add_product():
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client["shop"]
    products_collection = mongo_db["product"]
    product = request.json
    result = products_collection.insert_one(product)
    product['_id'] = str(result.inserted_id)
    return jsonify(product), 201


@app.route('/product', methods=['GET'])
def get_products():
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client["shop"]
    products_collection = mongo_db["product"]
    products = list(products_collection.find({}))
    for product in products:
        product['_id'] = str(product['_id'])
    return jsonify(products)


@app.route('/product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client["shop"]
    products_collection = mongo_db["product"]
    products_collection.delete_one({"_id": ObjectId(product_id)})
    return '', 204


@app.route('/worker', methods=['POST'])
def add_worker():
    postgres_conn = psycopg2.connect(POSTGRES_URI)
    postgres_cursor = postgres_conn.cursor()
    worker = request.json
    postgres_cursor.execute("INSERT INTO worker (firstname, lastname, post) VALUES (%s, %s, %s);",
                            (worker['firstname'], worker['lastname'], worker['post']))
    postgres_conn.commit()
    return jsonify(worker), 201


@app.route('/worker', methods=['GET'])
def get_worker():
    postgres_conn = psycopg2.connect(POSTGRES_URI)
    postgres_cursor = postgres_conn.cursor()
    postgres_cursor.execute("SELECT * FROM worker;")
    workers = postgres_cursor.fetchall()
    column_names = [desc[0] for desc in postgres_cursor.description]
    worker_list = [dict(zip(column_names, worker)) for worker in workers]
    return jsonify(worker_list)


@app.route('/worker/<worker_id>', methods=['DELETE'])
def delete_worker(worker_id):
    postgres_conn = psycopg2.connect(POSTGRES_URI)
    postgres_cursor = postgres_conn.cursor()
    postgres_cursor.execute("DELETE FROM worker WHERE id=%s;", worker_id)
    postgres_conn.commit()
    return '', 204


if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=8000, debug=True)
