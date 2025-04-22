import os
import json
import time
from django.http import StreamingHttpResponse
from django.shortcuts import render
from .models import ReportData
from .AI_Retriever import convertir_markdown_a_html
from ARCC_Api.models import AgentData
import markdown

from .AI_Retriever import (
    read_database_and_get_case, split_text_by_tokens, llm_interact_section_report,
    filter_cyber_compromise, filter_recent_files, detectar_tareas_sospechosas, dividir_texto_en_lotes, llm_interact_executive_report
)

def stream_reporte(request, case_id):
    def event_stream():
        max_tokens = 4096
        raw_data = AgentData.objects.filter(case_id=case_id).order_by('-id').first()
        if raw_data is None:
            yield "data: No se encontraron datos para el caso proporcionado.\n\n"
            return

        print(f"Datos obtenidos de la BD: {raw_data}")
        elements = [
            "Procesos En Ejecución", "Eventos de Sistema", "Inicio Automático",
            "Archivos Recientes", "Llaves de Registro de Sistema (Regedit)", "Tareas Programadas",
            "Conexiones de Red", "Reporte Ejecutivo"
        ]

        inicio = time.perf_counter()
        section_report = []

        # Procesos en ejecución
        yield "data: 1. Analizando Procesos...\n\n"
        process_read = json.dumps(raw_data.processes, indent=2)
        #process_read = json.dumps(json.loads(raw_data.get('processes')), indent=2)
        parts=[]
        if '{' in process_read and '}' in process_read:
            parts = split_text_by_tokens(process_read, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[0]))

        # Eventos de Seguridad
        yield "data: 2. Analizando Eventos de Seguridad...\n\n"
        events_read = raw_data.security_events.get('value')
        events_read = json.dumps(events_read, indent=2)
        parts=[]
        if '{' in events_read and '}' in events_read:
            parts = split_text_by_tokens(events_read, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[1]))

        # Programas de Inicio
        yield "data: 3. Analizando Programas de Inicio...\n\n"
        autostart = json.dumps(raw_data.startup_programs, indent=2)
        parts=[]
        if '{' in autostart and '}' in autostart:
            parts = split_text_by_tokens(autostart, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[2]))

        # Archivos Recientes
        yield "data: 4. Analizando Archivos Recientes...\n\n"
        recent_files = raw_data.recent_files.get('value')
        recent_files = json.dumps(filter_recent_files(recent_files), indent=2)
        parts=[]
        if '{' in recent_files and '}' in recent_files:
            parts = split_text_by_tokens(recent_files, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[3]))

        # Llaves de Registro
        yield "data: 5. Analizando Llaves de Registro...\n\n"
        registry_keys = raw_data.registry_keys
        registry_keys = json.dumps(registry_keys, indent=2)
        parts=[]
        if '{' in registry_keys and '}' in registry_keys:
            parts = split_text_by_tokens(registry_keys, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[4]))

        # Tareas Programadas
        yield "data: 6. Analizando Tareas Programadas...\n\n"
        scheduled_tasks = raw_data.scheduled_tasks.get('value')
        scheduled_tasks = json.dumps(detectar_tareas_sospechosas(scheduled_tasks), indent=2)
        parts=[]
        if '{' in scheduled_tasks and '}' in scheduled_tasks:
            parts = split_text_by_tokens(scheduled_tasks, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[5]))

        # Conexiones de Red
        yield "data: 7. Analizando Conexiones de Red...\n\n"
        dns_cache = json.dumps(raw_data.network_connections, indent=2)
        parts=[]
        if '{' in dns_cache and '}' in dns_cache:
            parts = split_text_by_tokens(dns_cache, max_tokens=max_tokens, overlap=200)
        section_report.append(llm_interact_section_report(parts, elements[6]))

        # Resumen Ejecutivo
        yield "data: 8. Creando Reporte Ejecutivo...\n\n"
        parts = []
        parts=dividir_texto_en_lotes(section_report)
        executive=llm_interact_executive_report(parts, elements[7])

        fin = time.perf_counter()
        duracion = fin - inicio
        #html_output = convertir_markdown_a_html(section_report)
        #print(f"HTML Output Generado:\n{html_output}")

        # Guardar en la base de datos
        ReportData.objects.create(
            case_id=case_id,
            processes_report=section_report[0],
            security_events_report=section_report[1],
            startup_programs_report=section_report[2],
            recent_files_report=section_report[3],
            registry_keys_report=section_report[4],
            scheduled_tasks_report=section_report[5],
            network_connections_report=section_report[6],
            executive_report=executive
        )

        tiempo_formateado = f"{int(duracion // 3600)}h {int((duracion % 3600) // 60)}m {duracion % 60:.2f}s"

        yield f"data: FINALIZADO|{tiempo_formateado}\n\n"


    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

def generador_reporte_view(request):
    return render(request, "case_id.html")

def mostrar_reporte_view(request, case_id):
    report_data = ReportData.objects.filter(case_id=case_id).order_by('-id').first()
    if report_data is None:
        return render(request, "no_data.html")

    context = {
        "case_id": case_id,
        "processes_report": markdown.markdown(report_data.processes_report),
        "security_events_report": markdown.markdown(report_data.security_events_report),
        "startup_programs_report": markdown.markdown(report_data.startup_programs_report),
        "recent_files_report": markdown.markdown(report_data.recent_files_report),
        "registry_keys_report": markdown.markdown(report_data.registry_keys_report),
        "scheduled_tasks_report": markdown.markdown(report_data.scheduled_tasks_report),
        "network_connections_report": markdown.markdown(report_data.network_connections_report),
        "executive_report": markdown.markdown(report_data.executive_report)
    }

    return render(request, "reporte.html", context)
