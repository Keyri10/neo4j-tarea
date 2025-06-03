from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase

app = Flask(__name__)
# Configuración correcta de CORS para permitir todas las solicitudes
CORS(app, resources={r"/*": {"origins": "*"}})


# Conexión a Neo4j - CORREGIDO: puerto 7687 para Bolt
NEO4J_URI = "neo4j+s://demo.neo4jlabs.com:7687"
NEO4J_USER = "recommendations"
NEO4J_PASS = "recommendations"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

@app.route('/recommendations/user/<user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    try:
        with driver.session(database="recommendations") as session:
            result = session.run("""
                MATCH (u:User {userId: $user_id})-[:RATED]->(m:Movie)
                WITH u, collect(m) as seen
                MATCH (m2:Movie)<-[:RATED]-(other:User)-[:RATED]->(m:Movie)
                WHERE NOT m2 IN seen
                RETURN DISTINCT m2.title as title, m2.movieId as movieId
                LIMIT 10
            """, user_id=user_id)
            movies = [record.data() for record in result]
        return jsonify(movies)
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/recommendations/movie/<movie_id>', methods=['GET'])
def get_movie_recommendations(movie_id):
    try:
        with driver.session(database="recommendations") as session:
            result = session.run("""
                MATCH (m:Movie {movieId: $movie_id})<-[:RATED]-(u:User)-[:RATED]->(rec:Movie)
                WHERE rec.movieId <> $movie_id
                RETURN DISTINCT rec.title as title, rec.movieId as movieId
                LIMIT 10
            """, movie_id=movie_id)
            movies = [record.data() for record in result]
        return jsonify(movies)
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500

# Ruta de prueba para verificar que el servidor está funcionando
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "API is running"})

# Ruta para obtener todos los usuarios (para pruebas)
@app.route('/users', methods=['GET'])
def get_users():
    try:
        with driver.session(database="recommendations") as session:
            result = session.run("""
                MATCH (u:User)
                RETURN u.userId as userId
                LIMIT 10
            """)
            users = [record.data() for record in result]
        return jsonify(users)
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500

# Ruta para obtener todas las películas (para pruebas)
@app.route('/movies', methods=['GET'])
def get_movies():
    try:
        with driver.session(database="recommendations") as session:
            result = session.run("""
                MATCH (m:Movie)
                RETURN m.title as title, m.movieId as movieId
                LIMIT 10
            """)
            movies = [record.data() for record in result]
        return jsonify(movies)
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Puerto cambiado a 3000
    app.run(debug=True, host='0.0.0.0', port=3000)