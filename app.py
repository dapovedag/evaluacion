from flask import Flask, render_template, send_file
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from io import BytesIO
import configparser
from sqlalchemy.engine import URL
import config

parametro = configparser.ConfigParser()
parametro.read(config.config_path)
server = parametro.get("database", "server")
database = parametro.get("database", "database")
db_driver = parametro.get("database", "driver")

connection_url = URL.create(
    "mssql+pyodbc",
    username="",
    password="",
    host=server,
    database=database,
    query={
        "driver": db_driver,
        "Trusted_Connection": "yes"
    },
)
engine = create_engine(connection_url)

app = Flask(__name__)

# Ruta principal que muestra el formulario para seleccionar el municipio
@app.route('/')
def index():
    # Obtener la lista de municipios de la base de datos
    municipios = pd.read_sql_query('SELECT DISTINCT pai_et_municipios FROM lectura_critica', engine)
    return render_template('index.html', municipios=municipios['pai_et_municipios'].tolist())

# Ruta para generar la gráfica
@app.route('/grafica')
def grafica():
    # Obtener datos de la base de datos
    df = pd.read_sql_query('SELECT pai_et_municipios, desempeno_1 FROM lectura_critica', engine)
    
    # Generar la gráfica
    fig, ax = plt.subplots()
    df.plot(x='pai_et_municipios', y='desempeno_1', kind='bar', ax=ax)
    plt.tight_layout()
    
    # Guardar la gráfica en un buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='jpg')
    buffer.seek(0)
    
    # Enviar la gráfica como archivo
    return send_file(buffer, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
