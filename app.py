"""
📄 app.py
El archivo app.py es el núcleo de la aplicación Flask. Define las rutas principales que permiten a los usuarios cargar archivos XML
desde un formulario web, procesarlos usando utilidades especializadas y devolver un archivo Excel generado para su descarga inmediata.
Su objetivo es coordinar el flujo de la aplicación, manejar las solicitudes HTTP y la comunicación entre el frontend y la lógica de negocio,
manteniendo el código organizado y enfocado en la interacción con el usuario.
"""

# Importa Flask y funciones para manejar solicitudes y archivos
from flask import Flask, render_template, request, send_file 
# Importa módulo OS para acceder a variables del sistema (como el puerto)
import os
# Importa la función personalizada que creaste para procesar XMLs
from utils.parse_cfdi import parse_cfdi, parse_cfdi_lote
from utils.pdf_editor_exporter import generar_excel_desde_campos
import pandas as pd
import io
from flask import jsonify, send_file, request





# Inicializa la aplicación Flask
app = Flask(__name__)
# Configura el tamaño máximo permitido para archivos cargados (5MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

@app.route('/exportar-editor', methods=['POST'])
def exportar_editor():
    try:
        # Recibir los datos desde JS (lista de selecciones con coordenadas)
        campos = request.get_json()

        # Convertir los datos a DataFrame
        df = pd.DataFrame(campos)

        # Crear Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Campos Seleccionados')

        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='factura_editada.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/exportar-campos', methods=['POST'])
def exportar_campos():
    try:
        campos = request.get_json()
        if not campos:
            return jsonify({"error": "No se recibieron campos"}), 400

        output, filename = generar_excel_desde_campos(campos)
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": f"Error al generar Excel: {str(e)}"}), 500

# Define la ruta principal del sitio ("/")
@app.route('/')
def index():
    # Muestra la plantilla HTML llamada 'index.html'
    return render_template('index.html')

@app.route('/editor')
def editor():
    return render_template('editor.html')

# Define una ruta que acepta solo solicitudes POST para subir archivos
@app.route('/subir', methods=['POST'])
def subir():
    # Obtiene el o los archivos sub       el formulario HTML
    archivos = request.files.getlist('archivo')
    # Valida que el archivo exista y que su nombre termine en '.xml'
    if not archivos or any(not archivo.filename.endswith('.xml') for archivo in archivos):
        return '❌ Todos los archivos deben ser formato XML.'

#Procesamiento del XML
    try:
# Leer todos los XMLs como bytes
        lista_de_xmls = [archivo.read() for archivo in archivos]

        # Si es solo un archivo, procesarlo individualmente
        if len(lista_de_xmls) == 1:
            output, nombre_archivo = parse_cfdi(lista_de_xmls[0])
        else:
            output, nombre_archivo = parse_cfdi_lote(lista_de_xmls)

        # Envía el archivo generado al navegador para que el usuario lo descargue
        return send_file(
            output,                      # Archivo en memoria
            as_attachment=True,          # Forzar la descarga
            download_name=nombre_archivo, # Nombre dinámico para el archivo
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' # Tipo de archivo Excel
        )
#Manejo de errores

    except Exception as e:
        # Si ocurre cualquier error durante el proceso, muestra un mensaje de error
        return f'❌ Error al procesar el XML: {str(e)}'

#Arranque del servidor
# Ejecuta la aplicación solo si el archivo se corre directamente (no importado como módulo)
if __name__ == '__main__':
    # Obtiene el puerto desde variables de entorno o usa 5000 como predeterminado
    port = int(os.environ.get("PORT", 5000))

    # Inicia la aplicación Flask en modo debug para desarrollo
    app.run(host='0.0.0.0', port=port, debug=True)