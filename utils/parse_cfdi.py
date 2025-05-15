"""
📂 utils/parse_cfdi.py
El archivo utils/parse_cfdi.py contiene la función encargada de procesar los archivos XML CFDI
(Comprobante Fiscal Digital por Internet). Su responsabilidad principal es extraer la información 
de los conceptos facturados y los datos generales del comprobante, para luego generar un archivo Excel 
en memoria que organiza esta información en dos hojas separadas. Esta función centraliza y separa toda 
la lógica de procesamiento del XML, manteniendo el código modular, reutilizable y más limpio para el proyecto.
"""
# utils/parse_cfdi.py

import io
import pandas as pd
from lxml import etree
from datetime import datetime
from typing import List


def parse_cfdi_lote(lista_de_xmls: List[bytes]):
    columnas_ordenadas = [
        'ClaveProdServ', 'NoIdentificacion', 'Cantidad', 'ClaveUnidad',
        'Unidad', 'Descripcion', 'ValorUnitario', 'Importe', 'ObjetoImp'
    ]
    todos_los_conceptos = []
    resumen_general = []

    for xml_bytes in lista_de_xmls:
        try:
            archivo_stream = io.BytesIO(xml_bytes)
            tree = etree.parse(archivo_stream)
            root = tree.getroot()

            version = root.attrib.get('Version', '')
            ns = {'cfdi': 'http://www.sat.gob.mx/cfd/3'} if '3.3' in version else {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

            conceptos = tree.xpath('//cfdi:Concepto', namespaces=ns)
            for concepto in conceptos:
                fila = {col: concepto.attrib.get(col, '') for col in columnas_ordenadas}
                todos_los_conceptos.append(fila)

            folio = root.attrib.get('Folio', '')
            fecha = root.attrib.get('Fecha', '')
            moneda = root.attrib.get('Moneda', '')
            total = root.attrib.get('Total', '')
            subtotal = root.attrib.get('SubTotal', '')

            emisor = tree.find('.//cfdi:Emisor', namespaces=ns)
            rfc_emisor = emisor.attrib.get('Rfc', '') if emisor is not None else ''
            nombre_emisor = emisor.attrib.get('Nombre', '') if emisor is not None else ''

            receptor = tree.find('.//cfdi:Receptor', namespaces=ns)
            rfc_receptor = receptor.attrib.get('Rfc', '') if receptor is not None else ''
            nombre_receptor = receptor.attrib.get('Nombre', '') if receptor is not None else ''

            resumen_general.append({
                'Folio': folio,
                'Fecha': fecha,
                'Moneda': moneda,
                'Subtotal': subtotal,
                'Total': total,
                'RFC Emisor': rfc_emisor,
                'Nombre Emisor': nombre_emisor,
                'RFC Receptor': rfc_receptor,
                'Nombre Receptor': nombre_receptor
            })

        except Exception as e:
            print(f"❌ Error al procesar un XML: {str(e)}")

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_conceptos = pd.DataFrame(todos_los_conceptos)
        df_generales = pd.DataFrame(resumen_general)
        df_conceptos.to_excel(writer, sheet_name='Conceptos', index=False)
        df_generales.to_excel(writer, sheet_name='Datos Generales', index=False)

        workbook = writer.book
        conceptos_sheet = writer.sheets['Conceptos']
        generales_sheet = writer.sheets['Datos Generales']

        conceptos_sheet.set_column('A:I', 20)
        generales_sheet.set_column('A:I', 20)

    output.seek(0)
    nombre_archivo = f"cfdi_lote_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return output, nombre_archivo


def parse_cfdi(xml_bytes):
    columnas_ordenadas = [
        'ClaveProdServ', 'NoIdentificacion', 'Cantidad', 'ClaveUnidad',
        'Unidad', 'Descripcion', 'ValorUnitario', 'Importe', 'ObjetoImp'
    ]

    archivo_stream = io.BytesIO(xml_bytes)
    tree = etree.parse(archivo_stream)
    root = tree.getroot()

    version = root.attrib.get('Version', '')
    namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/3'} if '3.3' in version else {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

    conceptos = tree.xpath('//cfdi:Concepto', namespaces=namespaces)
    datos = [{col: c.attrib.get(col, '') for col in columnas_ordenadas} for c in conceptos]
    df = pd.DataFrame(datos)

    folio = root.attrib.get('Folio', '')
    fecha = root.attrib.get('Fecha', '')
    moneda = root.attrib.get('Moneda', '')
    total = root.attrib.get('Total', '')
    subtotal = root.attrib.get('SubTotal', '')

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

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Conceptos', index=False)
        pd.DataFrame([info_extra]).to_excel(writer, sheet_name='Datos Generales', index=False)

        workbook = writer.book
        conceptos_sheet = writer.sheets['Conceptos']
        generales_sheet = writer.sheets['Datos Generales']

        conceptos_sheet.set_column('A:I', 20)
        generales_sheet.set_column('A:I', 20)

    output.seek(0)
    nombre_archivo = f"resultado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return output, nombre_archivo
