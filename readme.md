# Sistema experto Django para la asistencia técnica en mantenimiento de ascensores

Trabajo de Fin de Grado — Grado en Ingeniería Informática
Universidad Internacional de La Rioja (UNIR)
Autor: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

---

Sistema web desarrollado con Django que ayuda a los técnicos de
mantenimiento de ascensores durante las intervenciones correctivas.
El técnico selecciona los síntomas observados, el motor de inferencia
devuelve las causas más probables teniendo en cuenta el historial del
ascensor, y al cerrar la intervención se genera automáticamente el
parte de trabajo en PDF conforme al Real Decreto 355/2024 (ITC AEM 1).

---

## Requisitos previos

- Python 3.12 o superior
- Git

---

## Instalación

    git clone https://github.com/TU_USUARIO/tfg_ascensores.git
    cd tfg_ascensores

    python -m venv venv

    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate

    pip install -r requirements.txt
    python manage.py migrate
    python manage.py loaddata diagnostico/fixtures/datos_iniciales.json
    python manage.py createsuperuser
    python manage.py runserver

Abre el navegador en http://127.0.0.1:8000/login/

El comando `loaddata` carga los 5 subsistemas, 17 síntomas y 12 reglas
de diagnóstico iniciales. El Técnico Sénior puede ampliar la base de
conocimiento desde el panel de administración sin tocar el código.

---

## Primeros pasos

Antes de realizar intervenciones hay que configurar desde el panel
de administración (http://127.0.0.1:8000/admin/):

1. Crear un usuario técnico
2. Crear su perfil y asignarle el rol
3. Dar de alta al menos un ascensor
4. Asignar el ascensor al técnico

---

## Acceso desde móvil

Arranca el servidor con `python manage.py runserver 0.0.0.0:8000`,
averigua la IP local de tu ordenador con `ipconfig` (Windows) o
`ifconfig` (Mac/Linux) y accede desde el navegador del móvil a
`http://192.168.1.X:8000/login/`. El ordenador y el móvil deben
estar en la misma red WiFi.

Si Chrome en Android redirige a HTTPS y muestra error, escribe
explícitamente `http://` al principio de la URL.

---

## Pruebas

    pytest diagnostico/tests.py -v

---

## Tecnologías

| Tecnología | Versión |
|---|---|
| Python | 3.12 |
| Django | 6.0 |
| SQLite | Nativa |
| Bootstrap | 5.3 |
| xhtml2pdf | 0.2.16 |
| pytest-django | Latest |

---

## Licencia

MIT. Desarrollado como Trabajo de Fin de Grado en el Grado en
Ingeniería Informática de UNIR.