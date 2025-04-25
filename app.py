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
from utils.parse_cfdi import parse_cfdi  # 👈 Importamos parse_cfdi desde utils

# Inicializa la aplicación Flask
app = Flask(__name__)
# Configura el tamaño máximo permitido para archivos cargados (5MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
# Define la ruta principal del sitio ("/")
@app.route('/')
def index():
    # Muestra la plantilla HTML llamada 'index.html'
    return render_template('index.html')
# Define una ruta que acepta solo solicitudes POST para subir archivos
@app.route('/subir', methods=['POST'])
def subir():
    # Obtiene el archivo subido desde el formulario HTML
    archivo = request.files.get('archivo')
    # Valida que el archivo exista y que su nombre termine en '.xml'
    if not archivo or not archivo.filename.endswith('.xml'):
        return '❌ Formato de archivo no válido. Solo se aceptan XML.'

#Procesamiento del XML
    try:
        # Lee todo el contenido del archivo XML como bytes
        xml_bytes = archivo.read()

        # Procesa el contenido XML usando la función parse_cfdi (que devuelve archivo Excel y nombre)
        output, nombre_archivo = parse_cfdi(xml_bytes)
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