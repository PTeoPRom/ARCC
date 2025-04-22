import time
import pandas as pd
import sqlite3
import os
import json
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
import markdown
from .Summarize_Schedule_Tasks import detectar_tareas_sospechosas


# Cargar API Key desde el archivo .env
load_dotenv()
LLM_API_KEY = os.getenv("OPENAI_API_KEY")

# Función para leer la base de datos y obtener el caso por case_id
def read_database_and_get_case(db_path, case_id):
    """
    Lee la base de datos y obtiene el caso correspondiente al case_id proporcionado.

    Args:
        db_path (str): Ruta a la base de datos SQLite.
        case_id (str): ID del caso a buscar.

    Returns:
        dict: Diccionario con los datos del caso encontrado o un diccionario vacío si no se encuentra el caso.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ARCC_Api_agentdata WHERE case_id = ?", (case_id,))
        rows = cursor.fetchall()
        if not rows:
            print("No se encontraron entradas para el case_id proporcionado.")
            return {}
        df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
        max_id_entry = df.loc[df['id'].idxmax()]
        result_dict = max_id_entry.to_dict()
    except sqlite3.Error as e:
        print(f"Error al leer la base de datos: {e}")
        return {}
    finally:
        conn.close()
    return result_dict

# Función para contar los tokens en un mensaje
def count_tokens(message, model="gpt-4-turbo"):
    """
    Cuenta el número de tokens en un mensaje utilizando el modelo especificado.

    Args:
        message (str): Mensaje a contar los tokens.
        model (str): Modelo a utilizar para la codificación de tokens.

    Returns:
        int: Número de tokens en el mensaje.
    """
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(message)
    return len(tokens)

# Función para dividir un texto en fragmentos si excede el límite de tokens
def split_text_by_tokens(text, max_tokens=4096, overlap=500):
    """
    Divide un texto en fragmentos si excede el límite de tokens especificado, asegurando que los fragmentos
    comiencen y terminen en los límites de los objetos JSON.

    Args:
        text (str): Texto a dividir.
        max_tokens (int): Número máximo de tokens por fragmento.
        overlap (int): Número de tokens de superposición entre fragmentos.

    Returns:
        list: Lista de fragmentos de texto.
    """
    max_length = int(max_tokens * 0.8)
    num_parts = (count_tokens(text) // max_length) + 2
    parts = []
    part_length = len(text) // num_parts
    start = 0

    while start < len(text):
        end = start + part_length
        if end < len(text):
            # Ajustar el final al próximo '}' más cercano
            end = text.find('}', end) + 1
        if start > 0:
            # Ajustar el inicio al '{' más cercano antes del corte
            start = text.rfind('{', 0, start)
        parts.append(text[start:end])
        start = end - overlap  # Superposición

    return parts

# Función para generar reportes parciales acorde a cada mensaje que se envia
def llm_interact_partial_report(data):
    """
    Genera un reporte parcial interactuando con un modelo de lenguaje.

    Args:
        data (str): Datos a analizar.

    Returns:
        str: Reporte generado por el modelo de lenguaje.
    """
    client = OpenAI(api_key=LLM_API_KEY)
    prompt = f"""
    Eres un analista forense digital altamente especializado.

    Tu tarea es realizar un **análisis forense preliminar** sobre datos extraídos de un sistema comprometido para determinar si hay indicios de un **incidente cibernético**. 

    ### 🔎 Datos de entrada:
    ```
    {data}
    ```

    **Tarea:** 
    1. Analiza estos datos en busca de actividad maliciosa.
    2. Si identificas posibles compromisos, especifícalos y justifica por qué podrían ser maliciosos.
    3. Sugiere **acciones de respuesta y mitigación** en caso de una amenaza real.
    4. Si identificas archivos para su revisión manual, llaves de registro o tareas programadas, por favor indica sus rutas completas y sha-256
    5. Si no hay signos de ataque, indica por que no hay indicios de ataque.

    Entrega tu análisis en un formato técnico estructurado, priorizando hallazgos críticos.
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            store=True,
            messages=[
                {"role": "system", "content": "Eres un analista forense digital experto."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096
        )
        message = completion.choices[0].message.content
    except Exception as e:
        print(f"Error al interactuar con el modelo LLM: {e}")
        return ""
    return message

# Función que itera las distintas partes de los mensajes y unifica los distintos reportes
def llm_interact_section_report(data, item):
    """
    Interactúa con un modelo de lenguaje para generar un informe forense unificado basado en informes parciales.

    Args:
        data (list): Lista de datos de informes parciales a analizar.
        item (str): El elemento o tema del informe.

    Returns:
        str: Informe técnico estructurado generado por el modelo de lenguaje, o una cadena vacía si ocurre un error.
    """
    partial_reports = []
    for part in data:
        partial_reports.append(llm_interact_partial_report(part))
    partial_reports = str(partial_reports)
    prompt = f"""
    Eres un analista forense digital altamente especializado.
    
    Tu tarea es unificar estos reportes de información parcial que hacen referencia a ```{item}```

    ### Reportes parciales:
    ```
    {partial_reports}
    ```
    **Tarea:** 
    1. Analiza estos datos en busca de actividad maliciosa.
    2. Si identificas posibles compromisos, especifícalos y justifica por qué podrían ser maliciosos.
    3. Sugiere **acciones de respuesta y mitigación** en caso de una amenaza real.
    4. Si identificas archivos para su revisión manual, llaves de registro o tareas programadas, por favor indica sus rutas completas y sha-256
    5. Si no hay signos de ataque, indica por que no hay indicios de ataque.
    
    El titulo del reporte es Analisis de ```{item}``` o algo similar, ordenalo de tal forma que sea coherente.
    Como anotación no digas despues de revisar multiples reportes parciales, sino despues de revisar la información otorgada por el sistema o usa sentencias que vayan en ese sentido.

    Entrega tu análisis en un formato técnico estructurado, priorizando hallazgos críticos.
    """
    try:
        client = OpenAI(api_key=LLM_API_KEY)
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            store=True,
            messages=[
                {"role": "system", "content": "Eres un analista forense digital experto."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096
        )
        section_report = completion.choices[0].message.content
    except Exception as e:
        print(f"Error al interactuar con el modelo LLM: {e}")
        return ""
    return section_report

# Función para filtrar eventos
def filter_cyber_compromise(events):
    """
    Filtra eventos relevantes para identificar posibles compromisos cibernéticos.

    Args:
        events (list): Lista de eventos a filtrar.

    Returns:
        list: Lista de eventos filtrados relevantes.
    """
    critical_event_ids = {
        "4624", "4625", "4672", "4688", "4698", "4719", "4720", "4732", "4735", "4768"
    }
    relevant_fields = {
        "EventID", "TimeCreated", "Computer",
        "SubjectUserSid", "SubjectUserName", "SubjectLogonId",
        "TargetUserSid", "TargetUserName", "TargetDomainName",
        "NewProcessId", "NewProcessName", "ParentProcessName",
        "CommandLine", "LogonType", "IpAddress", "IpPort",
        "AuthenticationPackageName", "PrivilegeList"
    }
    filtered_events = []
    try:
        for event in events:
            if "Event" not in event:
                continue
            event_data = event["Event"]
            system_data = event_data.get("System", {})
            event_id = system_data.get("EventID")
            if event_id not in critical_event_ids:
                continue
            filtered_event = {
                "EventID": event_id,
                "TimeCreated": system_data.get("TimeCreated", {}).get("@SystemTime"),
                "Computer": system_data.get("Computer")
            }
            event_data_section = event_data.get("EventData", {})
            if event_data_section and isinstance(event_data_section.get("Data"), list):
                for field in event_data_section["Data"]:
                    field_name = field.get("@Name")
                    field_value = field.get("#text", "")
                    if field_name in relevant_fields:
                        filtered_event[field_name] = field_value
            filtered_events.append({"Event": filtered_event})
    except Exception as e:
        print(f"Error al filtrar eventos: {e}")
    return filtered_events

# Función para filtrar archivos sospechosos
def filter_recent_files(recent_files):
    """
    Filtra archivos recientes para identificar archivos sospechosos.

    Args:
        recent_files (list): Lista de archivos recientes a filtrar.

    Returns:
        list: Lista de archivos filtrados que son sospechosos.
    """
    suspicious_extensions = {".exe", ".bat", ".cmd", ".vbs", ".js", ".ps1", ".dll", ".sys"}
    filtered_files = []
    try:
        for file_entry in recent_files:
            file_path = file_entry["FullName"]
            file_len = file_entry["Length"]
            if file_len == None:
                continue
            if not any(file_path.endswith(ext) for ext in suspicious_extensions):
                continue
            filtered_files.append(file_entry)
    except Exception as e:
        print(f"Error al filtrar archivos recientes: {e}")
    return filtered_files

def convertir_markdown_a_html(secciones_md):
    """
    Convierte una lista de strings en formato Markdown a un string en HTML.

    :param secciones_md: Lista de strings en formato Markdown.
    :return: String con el contenido HTML resultante.
    """
    # Convertir cada sección de Markdown a HTML
    secciones_html = [markdown.markdown(seccion) for seccion in secciones_md]

    # Unir todas las secciones en un solo documento HTML
    return "\n".join(secciones_html)

# Funcion para generar reportes executivos de facil comprensión para cada personas que no tienen mayores conocimientos tecnicos
# Función para generar reportes parciales acorde a cada mensaje que se envia
def llm_interact_partial_executive_report(data):
    """
    Genera un reporte parcial interactuando con un modelo de lenguaje.

    Args:
        data (str): Datos a analizar.

    Returns:
        str: Reporte generado por el modelo de lenguaje.
    """
    client = OpenAI(api_key=LLM_API_KEY)
    prompt = f"""
    Eres un analista forense digital altamente especializado.  

    Tu tarea es generar un **reporte ejecutivo claro y accesible** a partir del análisis técnico de datos extraídos de un sistema comprometido.  

    **Objetivo:**  
    Traducir los hallazgos técnicos en un documento que cualquier persona, sin conocimientos en ciberseguridad, pueda entender. Debe ser amigable, directo y útil para la toma de decisiones.  

    *Datos de entrada:**  

    ```
    {data}
    ```

    **Tareas:**  

    1. **Análisis de Seguridad:** Revisa los datos y determina si hay indicios de una posible amenaza o actividad maliciosa.  
    2. **Resumen Ejecutivo:** Explica de manera sencilla qué ha ocurrido (si se detectó una amenaza), cuáles podrían ser las consecuencias y qué medidas se recomiendan tomar.  
    3. **Explicación No Técnica:** Evita términos altamente técnicos. Usa analogías o ejemplos cotidianos si es necesario.  
    4. **Plan de Acción:** Si se detecta una amenaza, proporciona recomendaciones claras y accionables.  
    5. **Tranquilidad o Advertencia:** Si no hay señales de compromiso, explica por qué el sistema parece seguro. Si hay riesgos, describe su impacto de forma clara y concisa.  

    **Estructura del Reporte Ejecutivo:**  

    - **Resumen General:** Breve descripción de la situación.  
    - **Hallazgos Clave:** ¿Hubo actividad sospechosa? ¿Cuál es el posible impacto?  
    - **Recomendaciones:** Pasos claros y accesibles para mitigar o prevenir riesgos.  
    - **Explicación en Términos Simples:** Usa lenguaje amigable para que cualquier persona pueda entender el riesgo y su importancia.  

    🔎 **Ejemplo de Formato Final:**  

    **Resumen General:**  
    "Hemos analizado los registros del sistema y hemos detectado indicios de actividad sospechosa que podrían comprometer la seguridad de la empresa."  

    **Hallazgos Clave:**  
    "Se encontraron archivos inusuales ejecutándose en horarios no habituales, lo que sugiere un posible acceso no autorizado."  

    **Recomendaciones:**  
    "Se recomienda cambiar inmediatamente las contraseñas y actualizar los sistemas de seguridad para evitar posibles ataques."  

    **IMPORTANTE:**  
    La prioridad es que cualquier persona pueda comprender el reporte sin conocimientos previos en informática. Evita jergas técnicas innecesarias.  


    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            store=True,
            messages=[
                {"role": "system", "content": "Eres un analista forense digital experto."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096
        )
        message = completion.choices[0].message.content
    except Exception as e:
        print(f"Error al interactuar con el modelo LLM: {e}")
        return ""
    return message

# Función que itera las distintas partes de los mensajes y unifica los distintos reportes
def llm_interact_executive_report(data, item):
    """
    Interactúa con un modelo de lenguaje para generar un informe forense unificado basado en informes parciales.

    Args:
        data (list): Lista de datos de informes parciales a analizar.
        item (str): El elemento o tema del informe.

    Returns:
        str: Informe técnico estructurado generado por el modelo de lenguaje, o una cadena vacía si ocurre un error.
    """
    partial_reports = []
    for part in data:
        partial_reports.append(llm_interact_partial_executive_report(part))
    partial_reports = str(partial_reports)
    prompt = f"""
    Eres un analista forense digital altamente especializado.  

    Tu tarea es unificar múltiples reportes ejecutivos parciales en un **reporte ejecutivo claro y accesible** a partir del análisis técnico de datos extraídos de un sistema comprometido.  

    **Objetivo:**  
    Traducir los hallazgos técnicos en un documento que cualquier persona, sin conocimientos en ciberseguridad, pueda entender. Debe ser amigable, directo y útil para la toma de decisiones.  

    **Datos de entrada:**  

    ```
    {partial_reports}
    ```

    **Tareas:**  

    1. **Análisis de Seguridad:** Revisa los datos y determina si hay indicios de una posible amenaza o actividad maliciosa.  
    2. **Resumen Ejecutivo:** Explica de manera sencilla qué ha ocurrido (si se detectó una amenaza), cuáles podrían ser las consecuencias y qué medidas se recomiendan tomar.  
    3. **Explicación No Técnica:** Evita términos altamente técnicos. Usa analogías o ejemplos cotidianos si es necesario.  
    4. **Plan de Acción:** Si se detecta una amenaza, proporciona recomendaciones claras y accionables.  
    5. **Tranquilidad o Advertencia:** Si no hay señales de compromiso, explica por qué el sistema parece seguro. Si hay riesgos, describe su impacto de forma clara y concisa.  
    6. **Listado de Malware:** Proporciona una lista del posible malware detectado en formato de tabla Markdown, clasificado por tipo.
    7. **Fecha de infección:** Proporciona la fecha de infección en formato de tabla Markdown.  

    **Estructura del Reporte Ejecutivo:**  

    - **Resumen General:** Breve descripción de la situación.  
    - **Hallazgos Clave:** ¿Hubo actividad sospechosa? ¿Cuál es el posible impacto?  
    - **Recomendaciones:** Pasos claros y accesibles para mitigar o prevenir riesgos.  
    - **Listado de Malware:**  

    | Tipo                | Posible Fecha de Infección |  
    |---------------------|----------------------------|  
    | Posible Spyware     | 2025-03-28                |  
    | Posible Malware     | 2025-04-10                |  
    | Posible Ransomware  | 2025-04-01                |  
    | Posible Trojan      | 2025-04-05                |  

    **IMPORTANTE:**  
    La prioridad es que cualquier persona pueda comprender el reporte sin conocimientos previos en informática. Evita jergas técnicas innecesarias.  

    """
    try:
        client = OpenAI(api_key=LLM_API_KEY)
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            store=True,
            messages=[
                {"role": "system", "content": "Eres un analista forense digital experto."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096
        )
        section_report = completion.choices[0].message.content
    except Exception as e:
        print(f"Error al interactuar con el modelo LLM: {e}")
        return ""
    return section_report

#Funcion para Unificar y hacer Split acorde al numero de Tokens para que todos los reportes se puedan procesar en un unico reporte ejecutivo
def dividir_texto_en_lotes(lista_textos, max_tokens=4096, umbral=0.8, model="gpt-4-turbo"):
    """
    Divide una lista de textos en fragmentos que no superen el 80% del límite de tokens permitido.

    Args:
        lista_textos (list): Lista de textos a dividir.
        max_tokens (int): Máximo número de tokens permitidos por la API (por defecto 4096).
        umbral (float): Porcentaje del límite de tokens que no se debe superar (por defecto 0.8).
        model (str): Modelo a utilizar para la codificación de tokens (por defecto "gpt-4-turbo").

    Returns:
        list: Lista de textos divididos en fragmentos adecuados.
    """
    limite_tokens = int(max_tokens * umbral)  # Cálculo del umbral de tokens
    lotes = []
    lote_actual = []
    tokens_actuales = 0

    for texto in lista_textos:
        tokens_texto = count_tokens(texto, model)  # Usamos la función externa para contar tokens

        # Si añadir este texto supera el límite, guardamos el lote actual y reiniciamos
        if tokens_actuales + tokens_texto > limite_tokens:
            if lote_actual:
                lotes.append(" ".join(lote_actual))
            lote_actual = [texto]
            tokens_actuales = tokens_texto
        else:
            lote_actual.append(texto)
            tokens_actuales += tokens_texto

    # Guardar el último lote si no está vacío
    if lote_actual:
        lotes.append(" ".join(lote_actual))

    return lotes

# Ejemplo de uso
if __name__ == "__main__":
    try:
        max_tokens=4096
        
        db_path = os.path.abspath(os.path.join(os.getcwd(), "..", "db.sqlite3"))
        case_id = input("Ingrese el case_id que desea buscar: ")
        raw_data = read_database_and_get_case(db_path, case_id)
        elements = [
            "Procesos En Ejecucion", "Eventos de Sistema", "Inicio Automatico",
            "Archivos Recientes", "LLaves de Registro de Sistema (Regedit)", "Tareas Programadas",
            "Conexiones de Red", "Reporte Ejecutivo"
        ]
        
        # Iniciar el contador
        inicio = time.perf_counter()
        
        print("1. Analizando Procesos ...")
        process_read = json.dumps(json.loads(raw_data.get('processes')), indent=2)
        parts = split_text_by_tokens(process_read, max_tokens=max_tokens, overlap=200)
        section_report = []
        section_report.append(llm_interact_section_report(parts, elements[0]))
        
        print("2. Analizando Eventos de Seguridad ...")
        events_read = json.loads(raw_data.get('security_events')).get('value')
        #events_read = json.dumps(events_read, indent=2)
        #events_read = json.dumps(filter_cyber_compromise(events_read), indent=2)
        events_read = json.dumps(events_read, indent=2)
        parts=[];
        if '{' in events_read and '}' in events_read:
            parts = split_text_by_tokens(events_read, max_tokens=max_tokens, overlap=200)            
        section_report.append(llm_interact_section_report(parts, elements[1]))
        
        print("3. Analizando Programas de Inicio ...")
        autostart = json.dumps(json.loads(raw_data.get('startup_programs')), indent=2)
        parts = split_text_by_tokens(autostart, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[2]))
                
        print("4. Analizando Archivos Recientes ...")
        ## Revisar Recent File, debido que no esta filtrando de manera adecuada
        recent_files = json.loads(raw_data.get('recent_files')).get('value')
        #recent_files = json.dumps(recent_files, indent=2)
        recent_files = json.dumps(filter_recent_files(recent_files), indent=2)
        parts = split_text_by_tokens(recent_files, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[3]))
        
        print("5. Analizando Llaves de Registro ...")
        registry_keys = json.loads(raw_data.get('registry_keys'))
        registry_keys = json.dumps(registry_keys, indent=2)
        parts = split_text_by_tokens(registry_keys, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[4]))
        
        print("6. Analizando Tareas Programadas ...")
        scheduled_tasks = json.loads(raw_data.get('scheduled_tasks')).get('value')
        #scheduled_tasks = json.dumps(scheduled_tasks, indent=2)
        scheduled_tasks = json.dumps(detectar_tareas_sospechosas(scheduled_tasks), indent=2)
        parts = split_text_by_tokens(scheduled_tasks, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[5]))
        
        print("7. Analizando Conexiones de Red ...")
        dns_cache = json.dumps(json.loads(raw_data.get("network_connections")), indent=2)
        parts = split_text_by_tokens(dns_cache, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[6]))
        
        print("8. Creando Reporte Ejecutivo ...")
        parts_executive=dividir_texto_en_lotes(section_report)
        executive_report=llm_interact_executive_report(parts_executive, elements[7])
        
        # Finalizar el contador
        fin = time.perf_counter()
        
        # Calcular la duración
        duracion = fin - inicio
        
        # Convertir a horas, minutos y segundos
        horas = int(duracion // 3600)
        minutos = int((duracion % 3600) // 60)
        segundos = duracion % 60

        # Mostrar resultado formateado
        print(f"Tiempo de ejecución: {horas}h {minutos}m {segundos:.2f}s")

        html_output=convertir_markdown_a_html(section_report)
        
    except Exception as e:
        print(f"Error en la ejecución del script: {e}")