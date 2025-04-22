### **Manual de Usuario del Sistema de Análisis Rapido de Compromiso Cibernetico**

---

## **Índice**
1. Introducción
2. Acceso al Sistema
3. Generación de Reportes
4. Visualización de Reportes
5. Interpretación de los Reportes
6. Resolución de Problemas Comunes
7. Contacto de Soporte

---

## **1. Introducción**
El sistema de análisis forense digital permite a los usuarios analizar datos de sistemas Windows para detectar posibles compromisos cibernéticos. A través de una interfaz web, puedes generar reportes técnicos y ejecutivos basados en datos recopilados por agentes remotos.

---

## **2. Acceso al Sistema**

1. **Abrir el Navegador Web:**
   - Ingresa la URL del servidor en la barra de direcciones del navegador. Ejemplo:
     ```
     http://<IP_DEL_SERVIDOR>:8000
     ```

2. **Página Principal:**
   - Serás redirigido a la página principal donde puedes generar reportes o visualizar reportes existentes.

---

## **3. Generación de Reportes**

1. **Acceder a la Página de Generación de Reportes:**
   - Haz clic en el enlace o botón que dice "Generar Reporte".

2. **Ingresar el ID del Caso:**
   - En la página de generación de reportes, ingresa el `ID del Caso` que deseas analizar. Este ID corresponde al caso que fue enviado por el agente remoto.

3. **Iniciar el Proceso:**
   - Haz clic en el botón "Generar Reporte".
   - El sistema comenzará a procesar los datos y generará un reporte en tiempo real.

4. **Progreso del Reporte:**
   - Durante el proceso, verás mensajes en tiempo real que indican el progreso del análisis (por ejemplo, "Analizando Procesos...", "Analizando Eventos de Seguridad...").

5. **Finalización:**
   - Una vez completado, el reporte estará disponible para su visualización.

---

## **4. Visualización de Reportes**

1. **Acceder a la Página de Reportes:**
   - Haz clic en el enlace o botón que dice "Ver Reporte".

2. **Seleccionar el ID del Caso:**
   - Ingresa el `ID del Caso` para el cual deseas visualizar el reporte.

3. **Contenido del Reporte:**
   - El reporte estará dividido en secciones como:
     - Procesos en Ejecución
     - Eventos de Seguridad
     - Programas de Inicio
     - Archivos Recientes
     - Llaves de Registro
     - Tareas Programadas
     - Conexiones de Red
     - Reporte Ejecutivo

4. **Formato del Reporte:**
   - Los reportes técnicos se presentan en formato detallado.
   - Los reportes ejecutivos están simplificados para facilitar su comprensión.

---

## **5. Interpretación de los Reportes**

### **1. Reporte Técnico**
- **Procesos en Ejecución:**
  - Muestra los procesos activos en el sistema.
  - Busca procesos sospechosos o desconocidos.
- **Eventos de Seguridad:**
  - Lista eventos recientes relacionados con la seguridad del sistema.
  - Identifica posibles intentos de acceso no autorizado.
- **Programas de Inicio:**
  - Muestra programas configurados para ejecutarse automáticamente al iniciar el sistema.
  - Busca programas no reconocidos o maliciosos.
- **Archivos Recientes:**
  - Lista archivos modificados recientemente.
  - Identifica archivos sospechosos o desconocidos.
- **Llaves de Registro:**
  - Muestra claves de registro sospechosas.
  - Busca configuraciones que puedan indicar malware.
- **Tareas Programadas:**
  - Lista tareas programadas en el sistema.
  - Identifica tareas sospechosas o no autorizadas.
- **Conexiones de Red:**
  - Muestra conexiones de red activas.
  - Busca conexiones a direcciones IP sospechosas.

### **2. Reporte Ejecutivo**
- Resumen simplificado de los hallazgos clave.
- Ideal para usuarios no técnicos o gerentes.

---

## **6. Resolución de Problemas Comunes**

### **1. No se Genera el Reporte**
- **Causa:** El `ID del Caso` ingresado no existe en la base de datos.
- **Solución:** Verifica que el agente haya enviado los datos correctamente y que el `ID del Caso` sea válido.

### **2. Mensaje de Error en la Página**
- **Causa:** Problema de conexión con el servidor o error interno.
- **Solución:**
  - Verifica que el servidor esté en ejecución.
  - Contacta al administrador del sistema.

### **3. Datos Incompletos en el Reporte**
- **Causa:** El agente no recopiló todos los datos necesarios.
- **Solución:** Asegúrate de que el agente se haya ejecutado correctamente en el sistema Windows.

---

## **7. Contacto de Soporte**

Si tienes problemas o preguntas, contacta al equipo de soporte técnico:

- **Email:** soporte@arcc-consultant.com
- **Teléfono:** +51 123 456 789
- **Horario de Atención:** Lunes a Viernes, 9:00 AM - 6:00 PM

---

Este manual está diseñado para guiarte en el uso del sistema de análisis forense digital. Si necesitas ayuda adicional, no dudes en contactar al equipo de soporte.
2. **Página Principal:**
   - Serás redirigido a la página principal donde puedes generar reportes o visualizar reportes existentes.

---

## **3. Generación de Reportes**

1. **Acceder a la Página de Generación de Reportes:**
   - Haz clic en el enlace o botón que dice "Generar Reporte".

2. **Ingresar el ID del Caso:**
   - En la página de generación de reportes, ingresa el `ID del Caso` que deseas analizar. Este ID corresponde al caso que fue enviado por el agente remoto.

3. **Iniciar el Proceso:**
   - Haz clic en el botón "Generar Reporte".
   - El sistema comenzará a procesar los datos y generará un reporte en tiempo real.

4. **Progreso del Reporte:**
   - Durante el proceso, verás mensajes en tiempo real que indican el progreso del análisis (por ejemplo, "Analizando Procesos...", "Analizando Eventos de Seguridad...").

5. **Finalización:**
   - Una vez completado, el reporte estará disponible para su visualización.

---

## **4. Visualización de Reportes**

1. **Acceder a la Página de Reportes:**
   - Haz clic en el enlace o botón que dice "Ver Reporte".

2. **Seleccionar el ID del Caso:**
   - Ingresa el `ID del Caso` para el cual deseas visualizar el reporte.

3. **Contenido del Reporte:**
   - El reporte estará dividido en secciones como:
     - Procesos en Ejecución
     - Eventos de Seguridad
     - Programas de Inicio
     - Archivos Recientes
     - Llaves de Registro
     - Tareas Programadas
     - Conexiones de Red
     - Reporte Ejecutivo

4. **Formato del Reporte:**
   - Los reportes técnicos se presentan en formato detallado.
   - Los reportes ejecutivos están simplificados para facilitar su comprensión.

---

## **5. Interpretación de los Reportes**

### **1. Reporte Técnico**
- **Procesos en Ejecución:**
  - Muestra los procesos activos en el sistema.
  - Busca procesos sospechosos o desconocidos.
- **Eventos de Seguridad:**
  - Lista eventos recientes relacionados con la seguridad del sistema.
  - Identifica posibles intentos de acceso no autorizado.
- **Programas de Inicio:**
  - Muestra programas configurados para ejecutarse automáticamente al iniciar el sistema.
  - Busca programas no reconocidos o maliciosos.
- **Archivos Recientes:**
  - Lista archivos modificados recientemente.
  - Identifica archivos sospechosos o desconocidos.
- **Llaves de Registro:**
  - Muestra claves de registro sospechosas.
  - Busca configuraciones que puedan indicar malware.
- **Tareas Programadas:**
  - Lista tareas programadas en el sistema.
  - Identifica tareas sospechosas o no autorizadas.
- **Conexiones de Red:**
  - Muestra conexiones de red activas.
  - Busca conexiones a direcciones IP sospechosas.

### **2. Reporte Ejecutivo**
- Resumen simplificado de los hallazgos clave.
- Ideal para usuarios no técnicos o gerentes.

---

## **6. Resolución de Problemas Comunes**

### **1. No se Genera el Reporte**
- **Causa:** El `ID del Caso` ingresado no existe en la base de datos.
- **Solución:** Verifica que el agente haya enviado los datos correctamente y que el `ID del Caso` sea válido.

### **2. Mensaje de Error en la Página**
- **Causa:** Problema de conexión con el servidor o error interno.
- **Solución:**
  - Verifica que el servidor esté en ejecución.
  - Contacta al administrador del sistema.

### **3. Datos Incompletos en el Reporte**
- **Causa:** El agente no recopiló todos los datos necesarios.
- **Solución:** Asegúrate de que el agente se haya ejecutado correctamente en el sistema Windows.

---

## **7. Contacto de Soporte**

Si tienes problemas o preguntas, contacta al equipo de soporte técnico:

- **Email:** seguinfo@j2ksec.com
- **Horario de Atención:** Lunes a Viernes, 9:00 AM - 6:00 PM

---