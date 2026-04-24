import os
import streamlit as st
import sqlite3
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def init_db():
    conn = sqlite3.connect('historial.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS preguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tecnologia TEXT,
            tipo TEXT,
            pregunta TEXT,
            respuesta TEXT
        )
    ''')
    conn.commit()
    conn.close()

def borrar_historial():
    conn = sqlite3.connect('historial.db')
    c = conn.cursor()
    c.execute('DELETE FROM preguntas')
    conn.commit()
    conn.close()


def guardar_pregunta(tecnologia, tipo, pregunta, respuesta):
    conn = sqlite3.connect('historial.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO preguntas (tecnologia, tipo, pregunta, respuesta)
        VALUES (?, ?, ?, ?)
    ''', (tecnologia, tipo, pregunta, respuesta))
    conn.commit()
    conn.close()

def obtener_historial():
    conn = sqlite3.connect('historial.db')
    c = conn.cursor()
    c.execute('SELECT tecnologia, tipo, pregunta, respuesta FROM preguntas ORDER BY id DESC')
    datos = c.fetchall()
    conn.close()
    return datos


init_db()

st.set_page_config(page_title="AI Interview Prep", page_icon="👨‍💻")
st.title("Entrevistador Técnico con IA")
st.write("Configura a tu entrevistador")

tab1, tab2 = st.tabs(["🎯 Generar Pregunta", "📚 Mi Historial"])

with tab1:
    st.subheader("Configuración")
    col1, col2 = st.columns(2)


    with col1:
        tecnologia = st.text_input("Tecnología:", placeholder="ej. Python, SQL, Java")

    with col2:
        tipo_pregunta = st.radio(
            "Tipo de preguntas:",
            ["Abiertas", "Test (Opción Múltiple)"],
            help="Elige si quieres desarrollar una respuesta o elegir entre varias opciones."
        )
    if st.button("Generar Pregunta", use_container_width=True):
        if tecnologia: 
            with st.spinner(f"Generando pregunta de tipo {tipo_pregunta.lower()}..."):
            
                if tipo_pregunta == "Abiertas":
                    prompt = prompt = f"""Actúa como un reclutador técnico senior. Hazme una única pregunta de entrevista abierta para un perfil junior de {tecnologia}. Debes responder ESTRICTAMENTE con este formato: [Tu pregunta aquí] --CORRECTA-- [La respuesta correcta explicada aquí]. Si no vas a generar una respuesta, cambia de pregunta, pero la única ejecución correcta es la anteriormente descrita."""
                else:
                    prompt = f"Actúa como un reclutador técnico senior. Hazme una única pregunta de tipo test (opción múltiple con 4 opciones: A, B, C, D) para un perfil junior de {tecnologia}. Deja un doble salto de línea (espacio en blanco) entre cada una de las opciones. Cada opción será una línea diferente. Despues de las 4 opciones añade OBLIGATORIAMENTE --CORRECTA-- seguido de la respuesta correcta. No me des introducción ni nada, sólamente pregunta y respuesta con ese formato"

            respuesta = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant", 
            )

            st.success("¡Pregunta lista!")
            st.markdown("---")
            res = respuesta.choices[0].message.content.split("--CORRECTA--")
            if len(res) > 1:
                guardar_pregunta(tecnologia, tipo_pregunta, res[0], res[1])
                st.session_state["pregunta_actual"] = res[0]
                st.session_state["respuesta_actual"] = res[1]
            if len(res) == 1:
                st.warning("Error de formato de la IA, por favor, vuelve a generar otra pregunta")
            
        else:
            st.warning("⚠️ Por favor, introduce una tecnología (ej. Java).")
    if "pregunta_actual" in st.session_state:
        st.info(st.session_state["pregunta_actual"])
        respuesta_usuario = st.text_area("Escribe tu respuesta aquí")
        if st.button("Enviar respuesta", use_container_width=True):
            prompt2 = f"""Te voy a pasar una pregunta y la respuesta que ha dado un alumno, vas a hacer de profesor. Devuelve una evaluación del 1 al 10 seguido de la explicación: Pregunta{st.session_state["pregunta_actual"]}, Respuesta del alumno:{respuesta_usuario}"""
            respuesta = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt2}],
                model="llama-3.1-8b-instant", 
            )

            st.success("Evaluación completada")
            correccion = respuesta.choices[0].message.content
            st.write(correccion)

with tab2:
    st.subheader("Tus preguntas guardadas")
    historial = obtener_historial()
    
    if len(historial) == 0:
        st.info("Aún no has generado ninguna pregunta.")
    else:
        
        for fila in historial:
            db_tec, db_tipo, db_preg, db_resp = fila
            
            
            with st.expander(f"[{db_tec}] - {db_tipo}"):
                st.markdown("**Pregunta:**")
                st.info(db_preg)
                st.markdown("**Respuesta:**")
                st.success(db_resp)

    if st.button("Borrar historial",use_container_width=True):
        borrar_historial()


