import os
import requests
from requests.auth import HTTPBasicAuth
import json
import urllib.parse
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class OpenProjectClient:
    def __init__(self):
        self.base_url = os.getenv("OPENPROJECT_URL")
        self.api_key = os.getenv("OPENPROJECT_API_KEY")
        
        if not self.base_url or not self.api_key:
            raise ValueError("Faltan variables de entorno OPENPROJECT_URL u OPENPROJECT_API_KEY")
            
        self.auth = HTTPBasicAuth("apikey", self.api_key)
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def _get_paginated(self, url):
        """Maneja paginación para cualquier endpoint"""
        results = []
        while url:
            try:
                response = requests.get(url, auth=self.auth, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                if '_embedded' in data:
                    results.extend(data['_embedded']['elements'])
                
                # Manejar URL próxima página
                next_url = data.get('_links', {}).get('nextByOffset', {}).get('href')
                url = f"{self.base_url}{next_url}" if next_url and not next_url.startswith('http') else None
                
            except Exception as e:
                print(f"Error en petición a API: {e}")
                break
        return results

    def get_projects(self):
        """Obtiene todos los proyectos"""
        return self._get_paginated(f"{self.base_url}/api/v3/projects")

    def get_time_entries(self, project_id):
        """Obtiene time entries de un proyecto"""
        filters = json.dumps([{'project_id': {'operator': '=', 'values': [str(project_id)]}}])
        encoded_filters = urllib.parse.quote(filters)
        return self._get_paginated(f"{self.base_url}/api/v3/time_entries?filters={encoded_filters}")

    def get_available_groups(self):
        """Obtiene todos los grupos del sistema"""
        return self._get_paginated(f"{self.base_url}/api/v3/groups")

    def get_user_groups(self, user_id):
        """Obtiene grupos de un usuario específico"""
        try:
            user_groups = []
            all_groups = self.get_available_groups()
            
            for group in all_groups:
                members = requests.get(
                    f"{self.base_url}/api/v3/groups/{group['id']}/members",
                    auth=self.auth,
                    headers=self.headers
                ).json().get('_embedded', {}).get('elements', [])
                
                if any(str(user_id) in member['_links']['self']['href'] for member in members):
                    user_groups.append(group)
            
            return user_groups
        except Exception as e:
            print(f"Error obteniendo grupos del usuario: {e}")
            return []