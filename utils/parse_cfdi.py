"""
📂 utils/parse_cfdi.py
El archivo utils/parse_cfdi.py contiene la función encargada de procesar los archivos XML CFDI
(Comprobante Fiscal Digital por Internet). Su responsabilidad principal es extraer la información 
de los conceptos facturados y los datos generales del comprobante, para luego generar un archivo Excel 
en memoria que organiza esta información en dos hojas separadas. Esta función centraliza y separa toda 
la lógica de procesamiento del XML, manteniendo el código modular, reutilizable y más limpio para el proyecto.
"""

# Importa io para manejar archivos directamente en memoria
import io

# Importa pandas para manipular datos en tablas y crear archivos Excel
import pandas as pd

# Importa lxml.etree para analizar y procesar archivos XML
from lxml import etree

# Importa datetime para generar nombres de archivos dinámicos con fecha y hora
from datetime import datetime

# Define la función parse_cfdi que procesa el XML recibido en bytes
def parse_cfdi(xml_bytes):
    """
    Recibe un XML CFDI en forma de bytes,
    extrae conceptos y datos generales,
    genera un archivo Excel en memoria,
    y retorna el archivo y su nombre sugerido.
    """

    # Crea un flujo de datos (archivo) en memoria a partir de los bytes recibidos
    archivo_stream = io.BytesIO(xml_bytes)

    # Parsea el XML usando lxml para convertirlo en un árbol de elementos
    tree = etree.parse(archivo_stream)

    # Obtiene el elemento raíz del XML
    root = tree.getroot()

    # Detecta la versión del CFDI (para aplicar el namespace correcto)
    version = root.attrib.get('Version', '')
    if '3.3' in version:
        namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/3'}
    else:
        namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

    # Busca todos los elementos 'Concepto' en el XML usando XPath y el namespace detectado
    conceptos = tree.xpath('//cfdi:Concepto', namespaces=namespaces)

    # Extrae todos los atributos de cada concepto en forma de diccionario
    datos = [concepto.attrib for concepto in conceptos]

    # Crea un DataFrame de pandas con la lista de conceptos
    df = pd.DataFrame(datos)

    # Accede a los atributos generales del comprobante (factura principal)
    comprobante = root
    folio = comprobante.attrib.get('Folio', '')  # Número de folio de la factura
    fecha = comprobante.attrib.get('Fecha', '')  # Fecha de emisión
    moneda = comprobante.attrib.get('Moneda', '')  # Moneda utilizada
    total = comprobante.attrib.get('Total', '')  # Total del comprobante
    subtotal = comprobante.attrib.get('SubTotal', '')  # Subtotal del comprobante

    # Extrae información del Emisor (quién factura)
    emisor = tree.find('.//cfdi:Emisor', namespaces=namespaces)
    rfc_emisor = emisor.attrib.get('Rfc', '') if emisor is not None else ''  # RFC del emisor
    nombre_emisor = emisor.attrib.get('Nombre', '') if emisor is not None else ''  # Nombre del emisor

    # Extrae información del Receptor (a quién se factura)
    receptor = tree.find('.//cfdi:Receptor', namespaces=namespaces)
    rfc_receptor = receptor.attrib.get('Rfc', '') if receptor is not None else ''  # RFC del receptor
    nombre_receptor = receptor.attrib.get('Nombre', '') if receptor is not None else ''  # Nombre del receptor

    # Crea un diccionario con todos los datos generales extraídos
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

    # Crea un nuevo archivo Excel directamente en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribe la tabla de conceptos en la hoja 'Conceptos'
        df.to_excel(writer, sheet_name='Conceptos', index=False)
        # Escribe los datos generales en la hoja 'Datos Generales'
        pd.DataFrame([info_extra]).to_excel(writer, sheet_name='Datos Generales', index=False)

    # Mueve el puntero del archivo Excel al principio para poder leerlo después
    output.seek(0)

    # Crea un nombre de archivo dinámico basado en la fecha y hora actual
    nombre_archivo = f"resultado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    # Retorna el archivo Excel en memoria y el nombre del archivo
    return output, nombre_archivo


