import io
import re
import sys
import openpyxl
from pathlib import Path
from datetime import datetime

def resource_path(relative_path):
    """Obtener ruta absoluta para el template"""
    base_path = Path(__file__).parent
    return base_path / relative_path

ROLES_ORDER = [
    "Gerente Unidad Proyectos", "Lider Gestión-2 Proyectos", "Ingeniero Gestión-1 Proyectos", "Ingeniero Gestión-2 Proyectos",
    "Gerente Unidad Desarrollo", "Senior Técnico-1 Desarrollo", "Lider Gestión-1 Desarrollo", "Ingeniero Técnico-1 Desarrollo",
    "Gerente Unidad Ingeniería", "Senior Técnico-1 Ingeniería",
    "Gerente Unidad Telco", "Senior Técnico-1 Telco"
]

def generate_excel_from_template(role_hours_list, project_name=None):
    # Usar resource_path para ubicar el template
    template_name = "Copia de NMX-PROYECTO-Analisis-Recursos v3.1.xlsx"
    template_path = resource_path(template_name)
    
    if not template_path.exists():
        raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
    
    try:
        # Cargar el libro de trabajo
        wb = openpyxl.load_workbook(str(template_path), data_only=False)
        ws = wb.active
        
        start_col = 9  # Columna I
        start_row = 9
        
        # Insertar valores
        for i, value in enumerate(role_hours_list):
            cell = ws.cell(row=start_row, column=start_col + i)
            cell.value = float(value)
            cell.number_format = '0.00'
        
        # Crear archivo en memoria
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)  # Ir al inicio del stream
        
        # Generar nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = (
            f"Calculadora_{project_name}_{timestamp}.xlsx" 
            if project_name 
            else f"Calculadora_{timestamp}.xlsx"
        )
        
        return output, filename
        
    except Exception as e:
        raise Exception(f"Error al procesar el archivo Excel: {str(e)}")
    
def parse_iso_duration(duration_str):
    """Convierte duración ISO 8601 a horas decimales"""
    pattern = r'PT(?:(?P<hours>\d+(?:\.\d+)?)H)?(?:(?P<minutes>\d+(?:\.\d+)?)M)?'
    match = re.fullmatch(pattern, duration_str) or {}
    hours = float(match.group('hours')) if match.group('hours') else 0.0
    minutes = float(match.group('minutes')) if match.group('minutes') else 0.0
    return round(hours + minutes / 60, 2)

def process_time_entries(entries):
    """Agrupa horas por usuario y recoge nombres"""
    hours_data = {}
    for entry in entries:
        user_link = entry.get('_links', {}).get('user', {})
        user_id = user_link.get('href', '').split('/')[-1] if isinstance(user_link, dict) else None
        hours = parse_iso_duration(entry.get('hours', 'PT0H'))
        
        if user_id:
            if user_id not in hours_data:
                hours_data[user_id] = {
                    'horas': 0.0,
                    'nombre': user_link.get('title', 'Desconocido')
                }
            hours_data[user_id]['horas'] += hours
    return hours_data

def prepare_assignment_data(time_entries, available_groups):
    """Prepara datos para asignación de roles"""
    hours_data = process_time_entries(time_entries)
    assignment_data = []
    
    for user_id, data in hours_data.items():
        user_groups = [
            g for g in available_groups 
            if any(member['href'].endswith(f"/users/{user_id}") 
                   for member in g.get('_links', {}).get('members', []))
        ]
        
        matching_roles = [g['name'] for g in user_groups if g['name'] in ROLES_ORDER]
        
        assignment_data.append({
            'user_id': user_id,
            'user_name': data['nombre'],
            'hours': data['horas'],
            'current_groups': [g['name'] for g in user_groups],
            'matching_roles': matching_roles
        })
    
    return assignment_data

def calculate_role_hours(assignments, hours_data):
    role_hours = {role: 0.0 for role in ROLES_ORDER}
    for user_id, role in assignments.items():
        role_hours[role] += hours_data.get(user_id, {}).get('horas', 0)
    return role_hours

def generate_excel_output(assignments, hours_data):
    role_hours = calculate_role_hours(assignments, hours_data)
    return "\t".join(str(round(role_hours[role], 2)) for role in ROLES_ORDER)