import json
import re

# Mapeo de claves en español e inglés
CLAVES = {
    "nombre_tarea": ["Nombre de tarea", "Task Name"],
    "usuario": ["Ejecutar como usuario", "Run As User"],
    "autor": ["Autor", "Author"],
    "comando": ["Tarea que se ejecutar ", "Action"],
    "tipo_programacion": ["Tipo de programación", "Trigger Type"],
}

# Palabras clave que indican inicio automático o persistencia
TIPOS_SOSPECHOSOS = [
    "Durante el inicio de sesión", "Cuando se inicie el sistema", "Cuando se produzca un evento",
    "At logon", "At system startup", "On an event"
]

# Expresión regular para detectar ubicaciones sospechosas (AppData, Temp, Roaming, Users, etc.)
UBICACIONES_SOSPECHOSAS = re.compile(
    r'(AppData|Temp|Roaming|Public|Users\\[^\\]+\\|\.exe$|\.bat$|\.vbs$|\.ps1$)', re.IGNORECASE
)

def limpiar_texto(texto):
    """Reemplaza caracteres truncados comunes en JSON generado por PowerShell"""
    if isinstance(texto, str):
        reemplazos = {
            "¢": "ó", "£": "ñ", "¥": "ü", "©": "é", "¡": "á", "¬": "í", "­": "ú", "ÿ": "m"
        }
        for clave, valor in reemplazos.items():
            texto = texto.replace(clave, valor)
        return texto
    return texto

def detectar_tareas_sospechosas(tareas):
    """
    Filtra tareas programadas sospechosas, manejando español e inglés y corrigiendo caracteres truncados.

    :param archivo_json: Ruta del archivo JSON con tareas programadas.
    :return: Lista de tareas sospechosas.
    """
    
    if not isinstance(tareas, list):
        raise TypeError("El parámetro 'tareas' debe ser una lista de diccionarios.")

    tareas_sospechosas = []

    for tarea in tareas:
        try:
            # Obtener valores de las claves en español o inglés
            nombre_tarea = next((tarea.get(k) for k in CLAVES["nombre_tarea"] if k in tarea), "")
            usuario = next((tarea.get(k) for k in CLAVES["usuario"] if k in tarea), "")
            autor = next((tarea.get(k) for k in CLAVES["autor"] if k in tarea), "")
            comando = next((tarea.get(k) for k in CLAVES["comando"] if k in tarea), "")
            tipo_programacion = next((tarea.get(k) for k in CLAVES["tipo_programacion"] if k in tarea), "")

            # Corregir caracteres truncados
            nombre_tarea = limpiar_texto(nombre_tarea)
            usuario = limpiar_texto(usuario)
            autor = limpiar_texto(autor)
            comando = limpiar_texto(comando)
            tipo_programacion = limpiar_texto(tipo_programacion)

            sospechoso = False
            razones = []

            # Criterio 1: Se ejecuta en inicio de sesión, sistema o evento
            if tipo_programacion in TIPOS_SOSPECHOSOS:
                sospechoso = True
                razones.append(f"Se ejecuta en: {tipo_programacion}")

            # Criterio 2: Ejecutado con permisos elevados (SYSTEM, Administrador)
            if usuario in ["SYSTEM", "Administrador", "Administrator", "Local Service", "Servicio Local"]:
                sospechoso = True
                razones.append(f"Ejecutada como usuario elevado: {usuario}")

            # Criterio 3: No tiene un autor válido
            if not autor or autor.lower() in ["n/a", "desconocido", "unknown"]:
                sospechoso = True
                razones.append("No tiene un autor válido")

            # Criterio 4: Ejecuta archivos desde ubicaciones sospechosas
            if UBICACIONES_SOSPECHOSAS.search(comando):
                sospechoso = True
                razones.append(f"Ejecuta desde ubicación sospechosa: {comando}")

            if sospechoso:
                tareas_sospechosas.append({
                    "Nombre de tarea": nombre_tarea,
                    "Ejecutar como usuario": usuario,
                    "Autor": autor,
                    "Tarea que se ejecuta": comando,
                    "Tipo de programación": tipo_programacion,
                    "Razones": razones
                })
        except Exception as e:
            print(f"Error procesando la tarea {tarea}: {e}")

    return tareas_sospechosas

""" # Uso de la función con el archivo JSON proporcionado
try:
    archivo_json = "/mnt/data/Scheduled_Task.json"
    with open(archivo_json, 'r', encoding='utf-8') as file:
        tareas = json.load(file)
    tareas_sospechosas = detectar_tareas_sospechosas(tareas)

    # Mostrar resultados en consola
    import pprint
    pprint.pprint(tareas_sospechosas)
except FileNotFoundError:
    print(f"El archivo {archivo_json} no se encontró.")
except json.JSONDecodeError:
    print(f"Error al decodificar el archivo JSON {archivo_json}.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}") """