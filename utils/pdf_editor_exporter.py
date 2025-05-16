import pandas as pd
import io
from datetime import datetime

def generar_excel_desde_campos(campos):
    """
    Recibe una lista de diccionarios con campos extraídos del editor.
    Cada diccionario debe tener claves como: etiqueta, valor, x, y, width, height
    """
    # Convertir la lista de campos a un DataFrame de pandas
    df = pd.DataFrame(campos)

    # Crear el archivo Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Campos Seleccionados', index=False)

        # Opcional: dar formato
        workbook = writer.book
        worksheet = writer.sheets['Campos Seleccionados']
        worksheet.set_column('A:E', 20)

    output.seek(0)
    nombre_archivo = f"editor_pdf_campos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return output, nombre_archivo
