# Calculadora de Proyectos NetMetrix

Aplicación para extraer y procesar horas trabajadas de OpenProject y generar reportes en Excel.

## Características Principales
- Conexión con OpenProject vía API
- Extracción de horas trabajadas por proyecto
- Generación de reportes estructurados en Excel
- Clasificación por roles predefinidos
- Interfaz web mediante Streamlit

## Requisitos Previos
- Python 3.9+
- Cuenta en OpenProject con permisos de API

## Estructura del Proyecto
├── .gitignore
├── app.py # Aplicación principal Streamlit
├── Copia de NMX-PROYECTO-Analisis-Recursos v3.1.xlsx # Plantilla Excel
├── data_processor.py # Lógica de procesamiento de datos
├── openproject_client.py # Cliente para API de OpenProject
├── README.md
└── requirements.txt # Dependencias


## 1. Configuración Inicial

### Variables de Entorno
La aplicación requiere estas variables:
- `OPENPROJECT_URL`: URL de tu instancia OpenProject
- `OPENPROJECT_API_KEY`: API Key de OpenProject

### Configuración Local (Desarrollo):
1. Crear archivo `.env` en el directorio raíz:
```bash
OPENPROJECT_URL=https://tu-instancia.openproject.com
OPENPROJECT_API_KEY=tu_api_key_123
```

### Configuración en servidor
#### Opción 1: Configuración temporal (bash)
```bash
export OPENPROJECT_URL=https://tu-instancia.openproject.com
export OPENPROJECT_API_KEY=tu_api_key_123
```
Nota: Esta configuración se perderá al cerrar la sesión de terminal.

#### Opción 2: Configuración persistente
##### A. En .bashrc (para el usuario actual)
```bash
echo 'export OPENPROJECT_URL="https://tu-instancia.openproject.com"' >> ~/.bashrc
echo 'export OPENPROJECT_API_KEY="tu_api_key_123"' >> ~/.bashrc
source ~/.bashrc
```
##### B. En systemd (recomendado para servicio) 
1. Crear un archivo de servicio en /etc/systemd/system/netmetrix.service:
```ini
[Unit]
Description=NetMetrix Calculator
After=network.target

[Service]
Environment="OPENPROJECT_URL=https://tu-instancia.openproject.com"
Environment="OPENPROJECT_API_KEY=tu_api_key_123"
ExecStart=/ruta/completa/venv/bin/streamlit run /ruta/completa/app.py
WorkingDirectory=/ruta/completa/
User=tu_usuario
Group=tu_grupo
Restart=always

[Install]
WantedBy=multi-user.target
```
2. Activar el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl start netmetrix
sudo systemctl enable netmetrix
```

## 2. Configuración en OpenProject
Crear estos grupos exactamente como se muestran:
- Gerente Unidad Proyectos 
- Lider Gestión-2 Proyectos
- Ingeniero Gestión-1 Proyectos
- Ingeniero Gestión-2 Proyectos
- Gerente Unidad Desarrollo
- Senior Técnico-1 Desarrollo
- Lider Gestión-1 Desarrollo
- Ingeniero Técnico-1 Desarrollo
- Gerente Unidad Ingeniería
- Senior Técnico-1 Ingeniería
- Gerente Unidad Telco
- Senior Técnico-1 Telco

##### Pasos en OpenProject:

1. Ir a "Administración" > "Grupos"
2. Crear cada grupo con los nombres exactos listados
3. Asignar usuarios a los grupos correspondientes

## Instalación y Ejecución

1. Clonar repositorio:
```bash
git clone https://github.com/Cordylus1/Calculadora_OpenProject.git
cd netmetrix-calculator
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar aplicación:
```bash
streamlit run app.py
```

## Despliegue en servidor

Recomendado para entornos productivos:

1. Instalar dependencias del sistema:
```bash
sudo apt-get install python3-pip python3-venv
```

2. Configurar entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configurar variables de entorno persistentes:
```bash
echo 'export OPENPROJECT_URL="https://tu-instancia.openproject.com"' >> ~/.bashrc
echo 'export OPENPROJECT_API_KEY="tu_api_key_123"' >> ~/.bashrc
source ~/.bashrc
```

4. Ejecutar como servicio (systemd):
Crear /etc/systemd/system/netmetrix.service:
```ini
[Unit]
Description=NetMetrix Calculator
After=network.target

[Service]
ExecStart=/ruta/completa/venv/bin/streamlit run /ruta/completa/app.py
WorkingDirectory=/ruta/completa/
User=tu_usuario
Group=tu_grupo
Restart=always

[Install]
WantedBy=multi-user.target
```

5. Iniciar servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl start netmetrix
sudo systemctl enable netmetrix
```

## Uso
1. Acceder a la interfaz web (puerto 8501 por defecto)

2. Seleccionar proyecto y rango de fechas

3. Generar reporte

4. Descargar archivo Excel resultante

## Notas Importantes
- Mantener el archivo Excel plantilla en el directorio raíz

- Verificar coincidencia de nombres de grupos en OpenProject

- Usar HTTPS para tráfico productivo

- Rotar API Keys periódicamente