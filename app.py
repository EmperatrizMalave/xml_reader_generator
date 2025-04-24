from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from lxml import etree
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Límite de 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('archivo')

    if not archivo or not archivo.filename.endswith('.xml'):
        return '❌ Formato de archivo no válido. Solo se aceptan XML.'

    try:
        # Guardar archivo subido
        ruta_xml = os.path.join(UPLOAD_FOLDER, archivo.filename)
        archivo.save(ruta_xml)

        # Parsear XML
        tree = etree.parse(ruta_xml)
        root = tree.getroot()

        # Detectar versión CFDI
        version = root.attrib.get('Version', '')
        if '3.3' in version:
            namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/3'}
        else:
            namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

        # Extraer conceptos
        conceptos = tree.xpath('//cfdi:Concepto', namespaces=namespaces)
        datos = [concepto.attrib for concepto in conceptos]
        df = pd.DataFrame(datos)

        # 🧾 Extraer datos generales del CFDI
        comprobante = root
        folio = comprobante.attrib.get('Folio', '')
        fecha = comprobante.attrib.get('Fecha', '')
        moneda = comprobante.attrib.get('Moneda', '')
        total = comprobante.attrib.get('Total', '')
        subtotal = comprobante.attrib.get('SubTotal', '')

        emisor = tree.find('.//cfdi:Emisor', namespaces=namespaces)
        rfc_emisor = emisor.attrib.get('Rfc', '') if emisor is not None else ''
        nombre_emisor = emisor.attrib.get('Nombre', '') if emisor is not None else ''

        receptor = tree.find('.//cfdi:Receptor', namespaces=namespaces)
        rfc_receptor = receptor.attrib.get('Rfc', '') if receptor is not None else ''
        nombre_receptor = receptor.attrib.get('Nombre', '') if receptor is not None else ''

        info_extra = {
            'Folio': folio,
            'Fecha': fecha,
            'Moneda': moneda,
            'Subtotal': subtotal,
            'Total': total,
            'RFC Emisor': rfc_emisor,
            'Nombre Emisor': nombre_emisor,
            'RFC Receptor': rfc_receptor,
            'Nombre Receptor': nombre_receptor
        }

        # 📁 Crear nombre único para el archivo Excel
        nombre_salida = f"resultado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ruta_excel = os.path.join(OUTPUT_FOLDER, nombre_salida)

        # ✍️ Guardar en dos hojas de Excel
        with pd.ExcelWriter(ruta_excel) as writer:
            df.to_excel(writer, sheet_name='Conceptos', index=False)
            pd.DataFrame([info_extra]).to_excel(writer, sheet_name='Datos Generales', index=False)

        return send_file(ruta_excel, as_attachment=True)

    except Exception as e:
        return f'❌ Error al procesar el XML: {str(e)}'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render proporciona PORT como variable de entorno
    app.run(host='0.0.0.0', port=port, debug=True)
