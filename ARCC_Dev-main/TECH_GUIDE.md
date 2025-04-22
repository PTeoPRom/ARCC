### **Manual Técnico del Sistema de Análisis Rapido de Compromiso Cibernetico**

---

## **Índice**
1. Introducción
2. Requisitos del Sistema
3. Estructura del Proyecto
4. Instalación y Configuración
5. Flujo de Trabajo
6. Componentes Principales
7. Endpoints de la API
8. Generación de Reportes
9. Mantenimiento y Extensión

---

## **1. Introducción**
Este sistema de análisis forense digital está diseñado para detectar posibles compromisos cibernéticos en sistemas Windows. Recopila datos críticos del sistema, los analiza utilizando un modelo de lenguaje (GPT-4) y genera reportes técnicos y ejecutivos para su revisión.

---

## **2. Requisitos del Sistema**

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

## **3. Estructura del Proyecto**
```
ARCC_Dev/
├── ARCC_Consultant/
│   ├── ARCC_Api/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   ├── ARCC_Dashboard/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── AI_Retriever.py
│   │   ├── templates/
│   │   │   ├── case_id.html
│   │   │   ├── reporte.html
│   │   │   ├── no_data.html
│   ├── ARCC_Consultant/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
├── ARCC_Agent/
│   ├── PS1 Code/
│   │   ├── agent.ps1
```

---

## **4. Instalación y Configuración**

### **Servidor**
1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/ffchequemarca/ARCC_Dev.git
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

## **5. Flujo de Trabajo**

1. **Recopilación de Datos:**
   - El agente PowerShell recopila datos del sistema y los envía al servidor.

2. **Almacenamiento:**
   - Los datos se almacenan en la tabla `AgentData` en la base de datos.

3. **Generación de Reportes:**
   - El usuario solicita un reporte desde la interfaz web.
   - El sistema analiza los datos utilizando GPT-4 y genera reportes técnicos y ejecutivos.

4. **Presentación:**
   - Los reportes se presentan en la interfaz web para su revisión.

---

## **6. Componentes Principales**

### **1. Backend**
- **`ARCC_Api`**
  - Maneja la API REST para recibir datos del agente.
  - Modelo: `AgentData` (almacena datos forenses).
- **`ARCC_Dashboard`**
  - Genera reportes basados en los datos almacenados.
  - Modelo: `ReportData` (almacena reportes generados).

### **2. Agente**
- **`agent.ps1`**
  - Recopila datos del sistema Windows y los envía al servidor.

### **3. Análisis con GPT-4**
- **`AI_Retriever.py`**
  - Interactúa con la API de OpenAI para analizar datos y generar reportes.

---

## **7. Endpoints de la API**

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

## **8. Generación de Reportes**

### **1. Reportes Técnicos**
- Analizan datos como procesos, eventos de seguridad, tareas programadas, etc.
- Generados por la función `llm_interact_section_report` en `AI_Retriever.py`.

### **2. Reportes Ejecutivos**
- Resumen simplificado para usuarios no técnicos.
- Generados por la función `llm_interact_executive_report` en `AI_Retriever.py`.

---

## **9. Mantenimiento y Extensión**

### **1. Actualización de Dependencias**
- Actualizar las dependencias periódicamente:
  ```bash
  pip install --upgrade -r requirements.txt
  ```

### **2. Migración de Base de Datos**
- Si se realizan cambios en los modelos:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### **3. Extensión del Sistema**
- **Agregar Nuevos Análisis:**
  - Crear nuevas funciones en `AI_Retriever.py`.
  - Actualizar las vistas en `ARCC_Dashboard/views.py`.
- **Soporte para Nuevos Agentes:**
  - Crear nuevos scripts para recopilar datos de otros sistemas operativos.

---

## **10. Contacto**
Para soporte técnico, contactar a:  
**Email:** csc1@j2ksec.com  
**Teléfono:** +57 314 212 0371
