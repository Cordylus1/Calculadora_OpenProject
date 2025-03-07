import streamlit as st
from openproject_client import OpenProjectClient
from data_processor import prepare_assignment_data, ROLES_ORDER, process_time_entries, generate_excel_output, calculate_role_hours, generate_excel_from_template
from datetime import datetime

# Configuración inicial de estado
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'selected_project_id' not in st.session_state:
    st.session_state.selected_project_id = None
if 'assignment_data' not in st.session_state:
    st.session_state.assignment_data = []
if 'user_assignments' not in st.session_state:
    st.session_state.user_assignments = {}
if 'user_hours' not in st.session_state:
    st.session_state.user_hours = {}

# Inicializar cliente de OpenProject
@st.cache_resource
def get_openproject_client():
    return OpenProjectClient()

client = get_openproject_client()

# Cargar proyectos si no están en caché
if not st.session_state.projects:
    try:
        projects = client.get_projects()
        st.session_state.projects = projects
    except Exception as e:
        st.error(f"Error cargando proyectos: {str(e)}")

# Interfaz principal
st.title("Calculadora de Proyecto")

# Selector de proyecto
project_names = [p['name'] for p in st.session_state.projects]
selected_project = st.selectbox(
    "Selecciona un proyecto",
    project_names,
    index=None,
    placeholder="Elige un proyecto..."
)

# Actualizar datos cuando cambia el proyecto
if selected_project:
    selected_project_id = next(p['id'] for p in st.session_state.projects if p['name'] == selected_project)
    
    if selected_project_id != st.session_state.selected_project_id:
        st.session_state.selected_project_id = selected_project_id
        st.session_state.assignment_data = []
        st.session_state.user_assignments = {}
        st.session_state.user_hours = {}
        
        try:
            time_entries = client.get_time_entries(selected_project_id)
            available_groups = client.get_available_groups()
            st.session_state.assignment_data = prepare_assignment_data(time_entries, available_groups)
            
            # Procesar horas
            hours_data = process_time_entries(time_entries)
            st.session_state.user_hours = {
                user_id: {'horas': data['horas']}
                for user_id, data in hours_data.items()
            }

            dates = []
            for entry in time_entries:
                if entry.get('spentOn'):
                    try:
                        date = datetime.strptime(entry['spentOn'], '%Y-%m-%d')
                        dates.append(date)
                    except ValueError:
                        pass
            
            if dates:
                start_date = min(dates)
                end_date = max(dates)
                total_days = (end_date - start_date).days + 1
                duration_months = total_days / 30  # 30 días por mes
                duration_months_rounded = round(duration_months, 1)
            else:
                duration_months_rounded = 0.0
            
            st.session_state.duration_months = duration_months_rounded


        except Exception as e:
            st.error(f"Error cargando datos del proyecto: {str(e)}")

# Mostrar tabla de miembros
if st.session_state.assignment_data:
    st.subheader("Integrantes del Proyecto")
    
    for idx, data in enumerate(st.session_state.assignment_data):
        user_id = data['user_id']
        user_name = data['user_name']
        hours = data['hours']
        matching_roles = data['matching_roles']
        
        # Determinar estado
        status_info = {
            0: ("Asignación manual requerida", "red"),
            1: ("Asignación automática", "green"),
            2: ("Múltiples roles detectados", "orange")
        }
        status = status_info[min(len(matching_roles), 2)]
        
        # Crear columnas para la fila
        col1, col2, col3, col4 = st.columns([3, 1, 2, 2])
        
        with col1:
            st.write(f"**{user_name}**")
        
        with col2:
            st.write(f"{hours:.2f} h")
        
        with col3:
            st.markdown(f"<span style='color:{status[1]}'>{status[0]}</span>", unsafe_allow_html=True)
        
        with col4:
            # Determinar opciones de roles
            if len(matching_roles) == 0:
                roles = ["Elegir..."] + ROLES_ORDER
            else:
                roles = matching_roles
                
            # Obtener selección actual
            current_role = st.session_state.user_assignments.get(user_id, "Elegir..." if len(matching_roles) == 0 else roles[0])
            
            # Crear selectbox
            selected_role = st.selectbox(
                f"Rol para {user_name}",
                roles,
                index=roles.index(current_role) if current_role in roles else 0,
                key=f"role_{user_id}"
            )
            
            # Actualizar asignaciones
            if selected_role != "Elegir...":
                st.session_state.user_assignments[user_id] = selected_role
            elif user_id in st.session_state.user_assignments:
                del st.session_state.user_assignments[user_id]

# Verificar si todas las asignaciones están completas
all_assigned = all(
    data['user_id'] in st.session_state.user_assignments
    for data in st.session_state.assignment_data
)

# Botones de acción
if all_assigned and st.session_state.assignment_data:
    try:
        role_hours = calculate_role_hours(st.session_state.user_assignments, st.session_state.user_hours)
        role_hours_list = [float(round(role_hours[role], 2)) for role in ROLES_ORDER]
        project_name = selected_project.replace(" ", "_")
        
        if st.button("Generar Calculadora Proyecto"):
            role_hours = calculate_role_hours(st.session_state.user_assignments, st.session_state.user_hours)
            role_hours_list = [float(round(role_hours[role], 2)) for role in ROLES_ORDER]
            project_name = selected_project.replace(" ", "_")
            
            excel_data, filename = generate_excel_from_template(
                role_hours_list, 
                project_name,
                st.session_state.get('duration_months', 0.0)
            )
            
            st.download_button(
                label="Descargar Excel",
                data=excel_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
    except Exception as e:
        st.error(f"Error generando Excel: {str(e)}")
else:
    st.warning("Por favor, asigna todos los roles antes de generar el Excel")