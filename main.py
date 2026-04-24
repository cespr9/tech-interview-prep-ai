import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


st.set_page_config(page_title="AI Interview Prep", page_icon="👨‍💻")
st.title("👨‍💻 Entrevistador Técnico con IA")
st.write("Configura tu sesión de estudio para el foro de empleo.")

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
                prompt = f"Actúa como un reclutador técnico senior. Hazme una única pregunta de tipo test (opción múltiple con 4 opciones: A, B, C, D) para un perfil junior de {tecnologia}. Cada opción será una línea diferente. Despues de las 4 opciones añade OBLIGATORIAMENTE --CORRECTA-- seguido de la respuesta correcta. No me des introducción ni nada, sólamente pregunta y respuesta con ese formato"

            respuesta = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant", 
            )

            st.success("¡Pregunta lista!")
            st.markdown("---")
            res = respuesta.choices[0].message.content.split("--CORRECTA--")
            if len(res) == 1:
                st.warning("Error de formato de la IA, por favor, vuelve a generar otra pregunta")
            else:
                st.info(res[0])
                with st.expander("👀 Mostrar Respuesta"):
                    st.write(res[1])
            
    else:
        st.warning("⚠️ Por favor, introduce una tecnología (ej. Java).")