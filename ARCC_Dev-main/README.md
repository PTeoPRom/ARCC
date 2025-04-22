### **README - ARCC Consultant**

---

## **Descripción del Proyecto**

ARCC Consultant es un sistema de análisis forense digital diseñado para detectar posibles compromisos cibernéticos en sistemas Windows. Este proyecto combina la recopilación de datos críticos del sistema, análisis avanzado utilizando inteligencia artificial (GPT-4), y generación de reportes técnicos y ejecutivos para facilitar la identificación de amenazas de seguridad.

---

## **Características Principales**

- **Recopilación de Datos del Sistema:**
  - Procesos en ejecución, conexiones de red, eventos de seguridad, tareas programadas, claves de registro, y más.
  
- **Análisis Automatizado:**
  - Utiliza GPT-4 para analizar los datos recopilados y generar reportes detallados.

- **Reportes Técnicos y Ejecutivos:**
  - Reportes técnicos para expertos en ciberseguridad.
  - Reportes ejecutivos simplificados para usuarios no técnicos.

- **Interfaz Web Intuitiva:**
  - Generación y visualización de reportes a través de una interfaz web.

- **API REST:**
  - Permite la integración con agentes remotos para enviar datos al servidor.

---

## **Estructura del Proyecto**

```
ARCC_Dev/
├── ARCC_Consultant/
│   ├── ARCC_Api/
│   │   ├── models.py        # Modelo para almacenar datos forenses
│   │   ├── views.py         # API REST para recibir datos
│   │   ├── urls.py          # Rutas de la API
│   ├── ARCC_Dashboard/
│   │   ├── models.py        # Modelo para almacenar reportes generados
│   │   ├── views.py         # Lógica para generar y mostrar reportes
│   │   ├── AI_Retriever.py  # Interacción con GPT-4 para análisis
│   │   ├── templates/       # Plantillas HTML para la interfaz web
│   ├── ARCC_Consultant/
│   │   ├── settings.py      # Configuración del proyecto Django
│   │   ├── urls.py          # Rutas principales del proyecto
│   │   ├── wsgi.py          # Configuración WSGI
├── ARCC_Agent/
│   ├── PS1 Code/
│   │   ├── agent.ps1        # Script PowerShell para recopilar datos
```

---

## **Requisitos del Sistema**

### **Servidor**
- **Sistema Operativo:** Linux (Ubuntu recomendado)
- **Python:** 3.10 o superior
- **Framework:** Django 5.1.6
- **Base de Datos:** SQLite (puede migrarse a PostgreSQL)
- **Dependencias:**
  - `django`
  - `djangorestframework`
  - `openai`
  - `markdown`
  - `python-dotenv`

### **Cliente (Agente)**
- **Sistema Operativo:** Windows 10 o superior
- **PowerShell:** Versión 5.1 o superior

---

## **Instalación**

### **Servidor**
1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd ARCC_Dev
   ```

2. **Crear un entorno virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   - Crear un archivo `.env` en el directorio raíz con el siguiente contenido:
     ```
     OPENAI_API_KEY=<TU_API_KEY_DE_OPENAI>
     ```

5. **Migrar la base de datos:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Ejecutar el servidor:**
   ```bash
   python manage.py runserver
   ```

### **Cliente (Agente)**
1. **Configurar el script PowerShell:**
   - Editar el archivo `agent.ps1` y configurar la URL del servidor:
     ```powershell
     $server_url = "http://<IP_DEL_SERVIDOR>/api/v1/agent_data/"
     ```

2. **Ejecutar el script en el sistema Windows:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File agent.ps1
   ```

---

## **Uso**

### **1. Generar un Reporte**
- Accede a la interfaz web en:
  ```
  http://<IP_DEL_SERVIDOR>:8000
  ```
- Ingresa el `ID del Caso` y haz clic en "Generar Reporte".

### **2. Visualizar un Reporte**
- Accede a la sección "Ver Reporte" en la interfaz web.
- Ingresa el `ID del Caso` para visualizar el reporte generado.

---

## **Endpoints de la API**

### **1. `POST /api/v1/agent_data/`**
- **Descripción:** Recibe datos forenses del agente.
- **Cuerpo de la solicitud:**
  ```json
  {
    "case_id": 123,
    "users": [...],
    "network_connections": [...],
    "processes": [...],
    "security_events": [...],
    "startup_programs": [...],
    "recent_files": [...],
    "scheduled_tasks": [...],
    "registry_keys": [...]
  }
  ```

### **2. `GET /stream_reporte/<case_id>/`**
- **Descripción:** Genera un reporte en tiempo real para un caso específico.

### **3. `GET /mostrar_reporte/<case_id>/`**
- **Descripción:** Muestra el reporte generado para un caso específico.

---

## **Contribución**

Si deseas contribuir al proyecto:
1. Haz un fork del repositorio.
2. Crea una rama para tu funcionalidad:
   ```bash
   git checkout -b nueva-funcionalidad
   ```
3. Realiza tus cambios y haz un commit:
   ```bash
   git commit -m "Descripción de los cambios"
   ```
4. Envía un pull request.

---

## **Licencia**

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## **Contacto**

Para soporte o consultas, contacta a:

- **Email:** seguinfo@j2ksec.com
- **Teléfono:** +57 314 212 0371

--- 

¡Gracias por usar ARCC Consultant!