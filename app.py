from flask import Flask, render_template, request, send_file
import os
import io # leer XML directamente desde la memoria
import pandas as pd
from lxml import etree
from datetime import datetime

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Límite de 5 MB

@app.route('/')
def index():
    return render_template('index.html')

# Ruta para subir y procesar el archivo XML
@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('archivo')  # Obtiene el archivo desde el formulario

    # Validación: que exista el archivo y sea .xml
    if not archivo or not archivo.filename.endswith('.xml'):
        return '❌ Formato de archivo no válido. Solo se aceptan XML.'

    try:
        # Leer el archivo XML directamente desde memoria sin guardarlo
        xml_bytes = archivo.read()              # Lee el contenido como bytes
        archivo_stream = io.BytesIO(xml_bytes)  # Convierte los bytes en un archivo en memoria

        # Parsear el XML directamente desde la memoria
        tree = etree.parse(archivo_stream)
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


        # generar Excel directamente en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Conceptos', index=False)
            pd.DataFrame([info_extra]).to_excel(writer, sheet_name='Datos Generales', index=False)
        output.seek(0)  # ✅ AGREGADO: mover puntero al inicio del archivo en memoria

        # crear nombre de descarga para el Excel
        nombre_descarga = f"resultado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # enviar archivo desde memoria directamente
        return send_file(
            output,
            as_attachment=True,
            download_name=nombre_descarga,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return f'❌ Error al procesar el XML: {str(e)}'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render proporciona PORT como variable de entorno
    app.run(host='0.0.0.0', port=port, debug=True)
