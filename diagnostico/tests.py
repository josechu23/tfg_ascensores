""""
Universidad Internacional de La Rioja
Escuela Superior de Ingeniería y Tecnología 
Grado en Ingeniería Informática
Sistema experto Django para la asistencia técnica en mantenimiento de ascensores.
Trabajo fin de estudio presentado por: José Manuel Palacios Hernández
Director: Luis Pedraza Gomara

tests.py - Pruebas unitarias y de integración del sistema experto
"""

import pytest
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from .models import (
    Ascensor, Subsistema, Sintoma, Regla,
    Intervencion, PerfilUsuario,
)
from .inference_engine import (
    obtener_diagnostico,
    serializar_diagnostico,
    deserializar_diagnostico,
)


class TestMotorInferencia(TestCase):
    """Pruebas unitarias del motor de inferencia (6 casos)."""

    def setUp(self):
        self.subsistema = Subsistema.objects.create(
            nombre='Puertas de prueba',
            descripcion='Subsistema creado para pruebas unitarias'
        )
        self.sintoma_1 = Sintoma.objects.create(
            subsistema=self.subsistema,
            descripcion='Síntoma de prueba 1', activo=True
        )
        self.sintoma_2 = Sintoma.objects.create(
            subsistema=self.subsistema,
            descripcion='Síntoma de prueba 2', activo=True
        )
        self.sintoma_3 = Sintoma.objects.create(
            subsistema=self.subsistema,
            descripcion='Síntoma de prueba 3', activo=True
        )
        # Regla que requiere síntoma_1 Y síntoma_2 simultáneamente.
        self.regla_1 = Regla.objects.create(
            nombre='Regla de prueba 1',
            subsistema=self.subsistema,
            causa_probable='Causa de prueba A',
            pasos_comprobacion='Paso 1 de prueba\nPaso 2 de prueba',
            criticidad='urgente', peso_base=2.0, activa=True
        )
        self.regla_1.sintomas_requeridos.set([self.sintoma_1, self.sintoma_2])

        # Regla que requiere solo síntoma_3.
        self.regla_2 = Regla.objects.create(
            nombre='Regla de prueba 2',
            subsistema=self.subsistema,
            causa_probable='Causa de prueba B',
            pasos_comprobacion='Paso único de prueba',
            criticidad='critico', peso_base=3.0, activa=True
        )
        self.regla_2.sintomas_requeridos.set([self.sintoma_3])

        self.ascensor = Ascensor.objects.create(
            identificador='TEST-001',
            direccion='Calle de Prueba 1',
            fabricante='Fabricante Test',
            tipo_ascensor='electrico_traccion', activo=True
        )
        self.usuario = User.objects.create_user(
            username='tecnico_test', password='password_test_123'
        )

    # TC01 — Activación correcta cuando todos los síntomas están presentes
    def test_motor_activa_regla_con_todos_los_sintomas(self):
        resultados = obtener_diagnostico(
            sintomas_ids=[self.sintoma_1.pk, self.sintoma_2.pk],
            ascensor_id=self.ascensor.pk
        )
        causas = [r['causa'] for r in resultados]
        self.assertIn('Causa de prueba A', causas)

    # TC02 — No activación cuando falta algún síntoma requerido
    def test_motor_no_activa_regla_con_sintomas_incompletos(self):
        resultados = obtener_diagnostico(
            sintomas_ids=[self.sintoma_1.pk],
            ascensor_id=self.ascensor.pk
        )
        causas = [r['causa'] for r in resultados]
        self.assertNotIn('Causa de prueba A', causas)

    # TC03 — Lista vacía cuando no se proporcionan síntomas
    def test_motor_devuelve_lista_vacia_sin_sintomas(self):
        resultados = obtener_diagnostico(
            sintomas_ids=[], ascensor_id=self.ascensor.pk
        )
        self.assertEqual(resultados, [])

    # TC04 — Ordenación de resultados de mayor a menor peso
    def test_motor_ordena_por_peso_descendente(self):
        resultados = obtener_diagnostico(
            sintomas_ids=[
                self.sintoma_1.pk, self.sintoma_2.pk, self.sintoma_3.pk
            ],
            ascensor_id=self.ascensor.pk
        )
        if len(resultados) >= 2:
            for i in range(len(resultados) - 1):
                self.assertGreaterEqual(
                    resultados[i]['peso_final'],
                    resultados[i + 1]['peso_final']
                )

    # TC05 — Ajuste de peso por historial del ascensor
    def test_motor_ajusta_peso_por_historial(self):
        Intervencion.objects.create(
            ascensor=self.ascensor,
            tecnico=self.usuario,
            causa_confirmada='Causa de prueba B',
            resultado='resuelto'
        )
        resultados = obtener_diagnostico(
            sintomas_ids=[self.sintoma_3.pk],
            ascensor_id=self.ascensor.pk
        )
        causa_b = next(
            (r for r in resultados if r['causa'] == 'Causa de prueba B'), None
        )
        self.assertIsNotNone(causa_b)
        self.assertGreater(causa_b['peso_final'], 3.0)

    # TC06 — Robustez ante JSON malformado en deserialización
    def test_deserializacion_json_invalido(self):
        resultado = deserializar_diagnostico('esto no es json válido {{{')
        self.assertEqual(resultado, [])


class TestModelos(TestCase):
    """Pruebas sobre el modelo de datos (4 casos)."""

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='test_modelos',
            first_name='Juan', last_name='García',
            password='password123'
        )
        self.perfil = PerfilUsuario.objects.create(
            usuario=self.usuario, rol='tecnico_campo'
        )
        self.ascensor = Ascensor.objects.create(
            identificador='MOD-001',
            direccion='Calle Modelos 1',
            fabricante='Test',
            tipo_ascensor='hidraulico', activo=True
        )

    # TC07 — Técnico de Campo no tiene permisos de sénior
    def test_perfil_tecnico_campo_no_es_senior(self):
        self.assertFalse(self.perfil.es_tecnico_senior())

    # TC08 — Técnico Sénior tiene permisos de sénior
    def test_perfil_tecnico_senior_es_senior(self):
        self.perfil.rol = 'tecnico_senior'
        self.perfil.save()
        self.assertTrue(self.perfil.es_tecnico_senior())

    # TC09 — Prueba de regresión: el rol administrador no existe
    def test_sistema_solo_tiene_dos_roles(self):
        roles = [choice[0] for choice in PerfilUsuario.ROL_CHOICES]
        self.assertEqual(len(roles), 2)
        self.assertNotIn('administrador', roles)

    # TC10 — Los ascensores inactivos no aparecen en consultas de activos
    def test_ascensor_inactivo_no_aparece_en_lista(self):
        ascensor_inactivo = Ascensor.objects.create(
            identificador='INACTIVO-001',
            direccion='Calle Inactiva 1',
            fabricante='Test',
            tipo_ascensor='hidraulico', activo=False
        )
        activos = Ascensor.objects.filter(activo=True)
        self.assertNotIn(ascensor_inactivo, activos)


class TestVistas(TestCase):
    """Pruebas de integración sobre las vistas HTTP (4 casos)."""

    def setUp(self):
        self.client = Client()
        self.usuario = User.objects.create_user(
            username='tecnico_vistas', password='password_vistas_123'
        )
        self.ascensor = Ascensor.objects.create(
            identificador='VISTA-001',
            direccion='Calle Vistas 1',
            fabricante='Test',
            tipo_ascensor='electrico_traccion', activo=True
        )
        self.ascensor.tecnicos.add(self.usuario)

    # TC11 — Sin sesión activa se redirige al login
    def test_login_requerido_para_ascensores(self):
        response = self.client.get(reverse('ascensor_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    # TC12 — Con sesión activa el listado de ascensores devuelve 200
    def test_lista_ascensores_visible_tras_login(self):
        self.client.login(
            username='tecnico_vistas', password='password_vistas_123'
        )
        response = self.client.get(reverse('ascensor_list'))
        self.assertEqual(response.status_code, 200)

    # TC13 — El formulario de síntomas es accesible para el técnico asignado
    def test_formulario_sintomas_accesible(self):
        self.client.login(
            username='tecnico_vistas', password='password_vistas_123'
        )
        response = self.client.get(
            reverse('sintomas_form', kwargs={'ascensor_id': self.ascensor.pk})
        )
        self.assertEqual(response.status_code, 200)

    # TC14 — Un ascensor inexistente devuelve 404
    def test_ascensor_inexistente_devuelve_404(self):
        self.client.login(
            username='tecnico_vistas', password='password_vistas_123'
        )
        response = self.client.get(
            reverse('sintomas_form', kwargs={'ascensor_id': 99999})
        )
        self.assertEqual(response.status_code, 404)