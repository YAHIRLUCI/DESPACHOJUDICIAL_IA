import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from docx import Document

app = Flask(__name__)
CORS(app)

DOCS_DIR = './documentos'
if not os.path.exists(DOCS_DIR): 
    os.makedirs(DOCS_DIR)

@app.route('/subir', methods=['POST'])
def subir():
    file = request.files['file']
    filepath = os.path.join(DOCS_DIR, file.filename)
    file.save(filepath)
    return jsonify({"mensaje": "Archivo guardado exitosamente"})

@app.route('/buscar', methods=['GET'])
def buscar():
    termino = request.args.get('q', '').lower()
    resultados = []
    # Busca en la carpeta principal y en todas las subcarpetas (ej. 2026/07)
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if termino in file.lower():
                ruta_relativa = os.path.relpath(os.path.join(root, file), DOCS_DIR)
                resultados.append({"nombre": file, "ruta": ruta_relativa})
    return jsonify(resultados)

@app.route('/leer', methods=['GET'])
def leer():
    ruta = request.args.get('ruta')
    ruta_completa = os.path.join(DOCS_DIR, ruta)
    try:
        extension = os.path.splitext(ruta_completa)[1].lower()
        contenido = ""

        if extension == '.docx':
            doc = Document(ruta_completa)
            contenido = "\n".join([para.text for para in doc.paragraphs])
        elif extension in ['.txt', '.csv']:
            with open(ruta_completa, 'r', encoding='utf-8') as f:
                contenido = f.read()
        else:
            return jsonify({"error": "Formato no soportado. Usa .txt o .docx"}), 400

        return jsonify({"contenido": contenido})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/resumir', methods=['POST'])
def resumir():
    data = request.json
    response = requests.post("http://localhost:1234/v1/chat/completions", json={
        "messages": [
            {"role": "system", "content": "Eres un abogado experto. Resume documentos con precisión legal."},
            {"role": "user", "content": f"Resume este texto legal: {data.get('texto')}"}
        ],
        "temperature": 0.3
    })
    return jsonify({"resumen": response.json()['choices'][0]['message']['content']})

@app.route('/exportar', methods=['POST'])
def exportar():
    data = request.json
    doc = Document()
    doc.add_paragraph(data.get('contenido'))
    doc.save('Resumen_Legal.docx')
    return send_file('Resumen_Legal.docx', as_attachment=True)

if __name__ == '__main__':
    app.run(port=5000)