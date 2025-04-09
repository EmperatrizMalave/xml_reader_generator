# Importamos las librerías necesarias
from flask import Flask, render_template, request, send_file  # Flask web + archivos
import os                                                    # Para rutas y carpetas
import pandas as pd                                          # Para trabajar con tablas y Excel
from lxml import etree                                       # Para leer el XML CFDI (SAT)

# Creamos la aplicación Flask
app = Flask(__name__)

# Definimos las carpetas para subir y guardar archivos
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

# Creamos las carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Ruta principal (GET) - Muestra el formulario HTML
@app.route('/')
def index():
    return render_template('index.html')  # Carga templates/index.html

# Ruta para subir y procesar el archivo XML (POST)
@app.route('/subir', methods=['POST'])
def subir():
    # Recibimos el archivo desde el formulario
    archivo = request.files['archivo']

    # Verificamos que sea un archivo XML
    if archivo.filename.endswith('.xml'):
        # Guardamos el archivo en la carpeta 'uploads'
        ruta_xml = os.path.join(UPLOAD_FOLDER, archivo.filename)
        archivo.save(ruta_xml)

        # Leemos el XML con lxml
        tree = etree.parse(ruta_xml)

        # Namespaces obligatorios para CFDI del SAT (3.3 y 4.0)
        namespaces = {
            'cfdi': 'http://www.sat.gob.mx/cfd/3',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
        }

        # Buscamos todos los nodos <cfdi:Concepto> en el XML
        conceptos = tree.xpath('//cfdi:Concepto', namespaces=namespaces)
        datos = []  # Aquí guardaremos los productos/servicios

        #  Recorremos cada concepto y guardamos sus atributos
        for concepto in conceptos:
            datos.append(concepto.attrib)  # .attrib = diccionario con datos del XML

        # Creamos una tabla (DataFrame) con pandas
        df = pd.DataFrame(datos)

        # Definimos la ruta de salida para el archivo Excel
        ruta_excel = os.path.join(OUTPUT_FOLDER, 'resultado.xlsx')

        # Exportamos el DataFrame a Excel
        df.to_excel(ruta_excel, index=False)

        # 📎 Enviamos el archivo Excel al navegador como descarga
        return send_file(ruta_excel, as_attachment=True)

    # Si no es XML, mostramos un mensaje
    return 'Formato de archivo no válido. Solo se aceptan XML.'

# Inicia la app Flask si ejecutamos `python app.py`
if __name__ == '__main__':
    app.run(debug=True)
