# Sistema Experto Django para la Asistencia Técnica en Mantenimiento de Ascensores

Trabajo de Fin de Grado — Grado en Ingeniería Informática  
Universidad Internacional de La Rioja (UNIR)  
Autor: Jose Manuel Palacios Hernández  
Director: Luis Pedraza Gomara

---

## Descripción

Sistema experto basado en reglas desarrollado con Django que apoya
a los técnicos de mantenimiento de ascensores durante las intervenciones
de mantenimiento correctivo. El sistema permite registrar síntomas de
avería, obtener un diagnóstico guiado con causas probables ordenadas
por probabilidad, registrar la intervención correctiva y generar el
parte de trabajo en PDF conforme a los requisitos del
Real Decreto 355/2024 (ITC AEM 1).

---

## Requisitos previos

Antes de instalar el proyecto necesitas tener instalado en tu equipo:

- Python 3.12 o superior
- Git

Para comprobar si los tienes instalados abre una terminal y ejecuta:

    python --version
    git --version

---

## Instalación paso a paso

### 1. Clonar el repositorio

    git clone https://github.com/TU_USUARIO/tfg_ascensores.git
    cd tfg_ascensores

### 2. Crear el entorno virtual

En Windows:

    python -m venv venv
    venv\Scripts\activate

En Mac/Linux:

    python -m venv venv
    source venv/bin/activate

Cuando el entorno virtual esté activo verás (venv) al principio
de la línea de la terminal.

### 3. Instalar las dependencias

    pip install -r requirements.txt

### 4. Aplicar las migraciones (crea la base de datos)

    python manage.py migrate

### 5. Cargar los datos iniciales (base de conocimiento)

Este comando carga en la base de datos los 5 subsistemas,
15 síntomas y 8 reglas de diagnóstico que forman la base
de conocimiento inicial del sistema experto:

    python manage.py loaddata diagnostico/fixtures/datos_iniciales.json

### 6. Crear el superusuario administrador

    python manage.py createsuperuser

Introduce el nombre de usuario, email y contraseña que quieras
cuando el sistema te lo pida.

### 7. Arrancar el servidor de desarrollo

    python manage.py runserver

Abre el navegador en http://127.0.0.1:8000/login/

---

## Estructura del proyecto

    tfg_ascensores/
    ├── config/                  <- Configuración del proyecto Django
    │   ├── settings.py          <- Parámetros de configuración
    │   └── urls.py              <- Enrutamiento principal de URLs
    ├── diagnostico/             <- Aplicación principal
    │   ├── fixtures/
    │   │   └── datos_iniciales.json  <- Base de conocimiento inicial
    │   ├── templates/
    │   │   └── diagnostico/     <- Plantillas HTML de la aplicación
    │   ├── admin.py             <- Configuración del panel de administración
    │   ├── inference_engine.py  <- Motor de inferencia (forward chaining)
    │   ├── models.py            <- Modelos de datos (base de datos)
    │   ├── report_generator.py  <- Generación de partes de trabajo en PDF
    │   ├── tests.py             <- Pruebas unitarias y de integración
    │   ├── urls.py              <- URLs de la aplicación
    │   └── views.py             <- Vistas (lógica de cada página)
    ├── static/
    │   └── diagnostico/
    │       └── css/
    │           └── custom.css   <- Estilos personalizados
    ├── templates/
    │   └── diagnostico/         <- Plantillas HTML del proyecto
    ├── manage.py                <- Comando principal de Django
    ├── pytest.ini               <- Configuración de pruebas
    └── requirements.txt         <- Dependencias Python del proyecto

---

## Acceso al sistema

Una vez arrancado el servidor hay dos puntos de acceso:

| URL | Descripción |
|-----|-------------|
| http://127.0.0.1:8000/login/ | Interfaz principal para técnicos |
| http://127.0.0.1:8000/admin/ | Panel de administración de Django |

Para acceder al panel de administración usa las credenciales
del superusuario que creaste en el paso 6.

---


---

## Acceso desde dispositivo móvil (smartphone o tablet)

El sistema está diseñado para ser utilizado desde dispositivos móviles
en campo. Para acceder desde un smartphone o tablet durante el desarrollo:

### Requisitos previos
- El dispositivo móvil y el ordenador deben estar conectados a la
  misma red WiFi.
- El servidor debe estar arrancado en el ordenador.

### Paso 1 — Averigua la IP local de tu ordenador

En Windows, abre una terminal y ejecuta:

    ipconfig

Busca la sección **Adaptador de LAN inalámbrica Wi-Fi** y anota
el valor de **Dirección IPv4**. Será algo como `192.168.1.X`.

En Mac/Linux:

    ifconfig | grep "inet "

### Paso 2 — Arranca el servidor escuchando en todas las interfaces

En lugar del comando habitual, usa:

    python manage.py runserver 0.0.0.0:8000

Esto hace que el servidor sea accesible desde cualquier dispositivo
de la red local, no solo desde el propio ordenador.

### Paso 3 — Accede desde el móvil

Abre el navegador del móvil y escribe:

    http://192.168.1.X:8000/login/

Sustituyendo `192.168.1.X` por la IP que obtuviste en el Paso 1.

### Nota importante sobre HTTPS en Chrome para Android

Chrome en Android puede forzar el protocolo HTTPS en conexiones
a direcciones IP locales, impidiendo el acceso mediante HTTP.
Si el navegador redirige automáticamente a https:// y muestra
un error de conexión, probar una de estas soluciones:

**Solución 1** — Escribe explícitamente `http://` al principio
de la URL en la barra de direcciones y pulsa ENTER.

**Solución 2** — Abre una pestaña nueva en Chrome, escribe
`chrome://flags` en la barra de direcciones, busca
`Insecure origins treated as secure`, actívalo y añade
`http://192.168.1.X:8000` a la lista. Reinicia Chrome.

> En un entorno de producción con certificado TLS válido este
> problema no existe, ya que la conexión sería HTTPS de forma nativa.

---

## Primeros pasos tras la instalación

Para poder usar el sistema es necesario configurar al menos:

1. Entrar en el panel de administración (http://127.0.0.1:8000/admin/)
2. Crear un usuario técnico en Autenticación > Usuarios
3. Crear su perfil en Diagnóstico > Perfiles de usuario y asignarle el rol
4. Dar de alta al menos un ascensor en Diagnóstico > Ascensores
5. Asignar el ascensor al técnico en el campo Técnicos asignados

---

## Ejecutar las pruebas

    pytest diagnostico/tests.py -v

---

## Tecnologías utilizadas

| Tecnología | Versión | Función |
|-----------|---------|---------|
| Python | 3.12 | Lenguaje de programación principal |
| Django | 5.0.6 | Framework web |
| SQLite | Nativa | Base de datos relacional |
| Bootstrap | 5.3 | Interfaz de usuario responsiva |
| ReportLab | 4.2.0 | Generación de documentos PDF |
| pytest | Latest | Pruebas unitarias y de integración |

---

## Licencia

Este proyecto ha sido desarrollado como Trabajo de Fin de Estudio
en el Grado en Ingeniería Informática de UNIR.
Publicado bajo licencia MIT.