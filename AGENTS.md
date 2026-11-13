# Contexto del Proyecto
Este es un monorepo para un SaaS de gestión de tareas. El backend usa Python/Django REST Framework y el frontend usa React con Vite. Todo está orquestado con Docker.

## Comandos de Desarrollo
- Levantar el entorno local: `docker compose up -d`
- Ver logs del backend: `docker compose logs -f backend`
- Entrar al shell de Django: `docker compose exec backend python manage.py shell`
- Crear migraciones: `docker compose exec backend python manage.py makemigrations`
- Instalar dependencia en frontend: `docker compose exec frontend npm install <paquete>`

## Reglas de Arquitectura y Estilo
### Backend (Django)
- **Cero HTML:** Django funciona estrictamente como una API REST. No uses `django.shortcuts.render` en ninguna vista.
- **Vistas:** Usa `APIView` o `ViewSets` de Django REST Framework (DRF) exclusivamente.
- **Autenticación:** Asume que la autenticación se maneja vía JWT (`djangorestframework-simplejwt`).

### Frontend (React/Vite)
- **Componentes:** Usa Functional Components con Hooks. Prohibido usar Class Components.
- **Estilos:** Usa Tailwind CSS para el estilado de componentes.
- **Estado:** Usa Zustand para el estado global y React Query para el fetching de datos hacia la API de Django.
- **Estructura:** Coloca la lógica de llamadas a la API (Axios/Fetch) dentro de la carpeta `src/services/`, no directamente en los componentes.