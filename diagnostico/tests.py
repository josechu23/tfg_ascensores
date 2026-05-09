import pytest
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from .models import Ascensor, Subsistema, Sintoma, Regla, Intervencion, PerfilUsuario
from .inference_engine import obtener_diagnostico, serializar_diagnostico, deserializar_diagnostico


class TestMotorInferencia(TestCase):

    def setUp(self):
        self.subsistema = Subsistema.objects.create(nombre='Puertas de prueba')
        self.s1 = Sintoma.objects.create(subsistema=self.subsistema, descripcion='Síntoma 1', activo=True)
        self.s2 = Sintoma.objects.create(subsistema=self.subsistema, descripcion='Síntoma 2', activo=True)
        self.s3 = Sintoma.objects.create(subsistema=self.subsistema, descripcion='Síntoma 3', activo=True)

        self.regla_a = Regla.objects.create(
            nombre='Regla A', subsistema=self.subsistema,
            causa_probable='Causa A', pasos_comprobacion='Paso 1\nPaso 2',
            criticidad='urgente', peso_base=2.0, activa=True
        )
        self.regla_a.sintomas_requeridos.set([self.s1, self.s2])

        self.regla_b = Regla.objects.create(
            nombre='Regla B', subsistema=self.subsistema,
            causa_probable='Causa B', pasos_comprobacion='Paso único',
            criticidad='critico', peso_base=3.0, activa=True
        )
        self.regla_b.sintomas_requeridos.set([self.s3])

        self.ascensor = Ascensor.objects.create(
            identificador='TEST-001', direccion='Calle Test 1',
            fabricante='Test', tipo_ascensor='electrico_traccion', activo=True
        )
        self.usuario = User.objects.create_user(username='tecnico_test', password='pass123')

    def test_activa_regla_con_sintomas_correctos(self):
        resultados = obtener_diagnostico([self.s1.pk, self.s2.pk], self.ascensor.pk)
        self.assertIn('Causa A', [r['causa'] for r in resultados])

    def test_no_activa_regla_con_sintomas_incompletos(self):
        resultados = obtener_diagnostico([self.s1.pk], self.ascensor.pk)
        self.assertNotIn('Causa A', [r['causa'] for r in resultados])

    def test_devuelve_vacio_sin_sintomas(self):
        self.assertEqual(obtener_diagnostico([], self.ascensor.pk), [])

    def test_ordena_resultados_por_peso(self):
        resultados = obtener_diagnostico([self.s1.pk, self.s2.pk, self.s3.pk], self.ascensor.pk)
        for i in range(len(resultados) - 1):
            self.assertGreaterEqual(resultados[i]['peso_final'], resultados[i+1]['peso_final'])

    def test_ajusta_peso_con_historial(self):
        Intervencion.objects.create(
            ascensor=self.ascensor, tecnico=self.usuario,
            causa_confirmada='Causa B', resultado='resuelto'
        )
        resultados = obtener_diagnostico([self.s3.pk], self.ascensor.pk)
        causa_b = next((r for r in resultados if r['causa'] == 'Causa B'), None)
        self.assertIsNotNone(causa_b)
        self.assertGreater(causa_b['peso_final'], 3.0)

    def test_deserializacion_json_invalido(self):
        self.assertEqual(deserializar_diagnostico('{{{no es json'), [])


class TestModelos(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(username='test_mod', first_name='Juan', last_name='García', password='pass123')
        self.perfil  = PerfilUsuario.objects.create(usuario=self.usuario, rol='tecnico_campo')
        self.ascensor = Ascensor.objects.create(
            identificador='MOD-001', direccion='Calle Modelos 1',
            fabricante='Test', tipo_ascensor='hidraulico', activo=True
        )

    def test_tecnico_campo_no_es_senior(self):
        self.assertFalse(self.perfil.es_tecnico_senior())

    def test_tecnico_senior_es_senior(self):
        self.perfil.rol = 'tecnico_senior'
        self.perfil.save()
        self.assertTrue(self.perfil.es_tecnico_senior())

    def test_solo_existen_dos_roles(self):
        roles = [c[0] for c in PerfilUsuario.ROL_CHOICES]
        self.assertEqual(len(roles), 2)
        self.assertNotIn('administrador', roles)

    def test_ascensor_inactivo_no_aparece_en_activos(self):
        inactivo = Ascensor.objects.create(
            identificador='INACT-001', direccion='Calle Inactiva 1',
            fabricante='Test', tipo_ascensor='hidraulico', activo=False
        )
        self.assertNotIn(inactivo, Ascensor.objects.filter(activo=True))


class TestVistas(TestCase):

    def setUp(self):
        self.client  = Client()
        self.usuario = User.objects.create_user(username='tecnico_v', password='pass123')
        self.ascensor = Ascensor.objects.create(
            identificador='VISTA-001', direccion='Calle Vistas 1',
            fabricante='Test', tipo_ascensor='electrico_traccion', activo=True
        )
        self.ascensor.tecnicos.add(self.usuario)

    def test_redirige_a_login_sin_sesion(self):
        response = self.client.get(reverse('ascensor_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_lista_ascensores_con_login(self):
        self.client.login(username='tecnico_v', password='pass123')
        self.assertEqual(self.client.get(reverse('ascensor_list')).status_code, 200)

    def test_formulario_sintomas_accesible(self):
        self.client.login(username='tecnico_v', password='pass123')
        response = self.client.get(reverse('sintomas_form', kwargs={'ascensor_id': self.ascensor.pk}))
        self.assertEqual(response.status_code, 200)

    def test_ascensor_inexistente_devuelve_404(self):
        self.client.login(username='tecnico_v', password='pass123')
        response = self.client.get(reverse('sintomas_form', kwargs={'ascensor_id': 99999}))
        self.assertEqual(response.status_code, 404)
