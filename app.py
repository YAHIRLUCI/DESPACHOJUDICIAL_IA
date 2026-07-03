import os
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from docx import Document

app = Flask(__name__)
CORS(app)

DOCS_DIR = './documentos'

if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)


# ===========================
# SUBIR ARCHIVO
# ===========================

@app.route('/subir', methods=['POST'])
def subir():

    file = request.files['file']

    filepath = os.path.join(DOCS_DIR, file.filename)

    file.save(filepath)

    return jsonify({
        "mensaje": "Archivo guardado exitosamente"
    })


# ===========================
# BUSCAR ARCHIVOS
# ===========================

@app.route('/buscar', methods=['GET'])
def buscar():

    termino = request.args.get('q', '').lower()

    tipo = request.args.get('tipo', '').lower()

    fecha = request.args.get('fecha', '')

    resultados = []

    # Buscar en todas las carpetas

    for root, dirs, files in os.walk(DOCS_DIR):

        for file in files:

            ruta_archivo = os.path.join(root, file)

            ruta_relativa = os.path.relpath(ruta_archivo, DOCS_DIR)

            # Obtener extensión

            extension = os.path.splitext(file)[1].replace(".", "").lower()

            # Obtener fecha de modificación

            fecha_archivo = datetime.fromtimestamp(
                os.path.getmtime(ruta_archivo)
            ).strftime("%Y-%m-%d")

            # ---------------------------
            # FILTRO POR NOMBRE
            # ---------------------------

            if termino:

                if termino not in file.lower():

                    continue

            # ---------------------------
            # FILTRO POR TIPO
            # ---------------------------

            if tipo:

                if extension != tipo:

                    continue

            # ---------------------------
            # FILTRO POR FECHA
            # ---------------------------

            if fecha:

                if fecha_archivo != fecha:

                    continue

            resultados.append({

                "nombre": file,

                "ruta": ruta_relativa,

                "tipo": extension,

                "fecha": fecha_archivo

            })

    return jsonify(resultados)


# ===========================
# LEER DOCUMENTO
# ===========================

@app.route('/leer', methods=['GET'])
def leer():

    ruta = request.args.get('ruta')

    ruta_completa = os.path.join(DOCS_DIR, ruta)

    try:

        extension = os.path.splitext(ruta_completa)[1].lower()

        contenido = ""

        if extension == '.docx':

            doc = Document(ruta_completa)

            contenido = "\n".join(
                [para.text for para in doc.paragraphs]
            )

        elif extension in ['.txt', '.csv']:

            with open(ruta_completa, 'r', encoding='utf-8') as f:

                contenido = f.read()

        else:

            return jsonify({
                "error": "Formato no soportado. Usa .txt o .docx"
            }), 400

        return jsonify({
            "contenido": contenido
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ===========================
# RESUMIR CON IA
# ===========================

@app.route('/resumir', methods=['POST'])
def resumir():

    data = request.json

    response = requests.post(

        "http://localhost:1234/v1/chat/completions",

        json={

            "messages": [

                {
                    "role": "system",
                    "content": "Eres un abogado experto. Resume documentos con precisión legal."
                },

                {
                    "role": "user",
                    "content": f"Resume este texto legal: {data.get('texto')}"
                }

            ],

            "temperature": 0.3

        }

    )

    return jsonify({

        "resumen": response.json()['choices'][0]['message']['content']

    })


# ===========================
# EXPORTAR A WORD
# ===========================

@app.route('/exportar', methods=['POST'])
def exportar():

    data = request.json

    doc = Document()

    doc.add_paragraph(

        data.get('contenido')

    )

    doc.save('Resumen_Legal.docx')

    return send_file(

        'Resumen_Legal.docx',

        as_attachment=True

    )


# ===========================
# INICIAR SERVIDOR
# ===========================

if __name__ == '__main__':

    app.run(port=5000)