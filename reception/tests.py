from django.test import TestCase
from django.core.exceptions import ValidationError
from users.models import Patient


# Verificación del campo CI (identification_number)
class PatientModelValidationTest(TestCase):
    def test_identification_number_only_digits_field_validator_returns_clean_value(self):
        """
        field.clean(...) devuelve el valor limpiado; aquí comprobamos que para una
        entrada válida se devuelve el mismo string de dígitos.
        """
        field = Patient._meta.get_field('identification_number')
        cleaned = field.clean('1234567890', None)
        self.assertEqual(cleaned, '1234567890')

    def test_identification_number_only_digits_field_validator_rejects_non_digits(self):
        """
        Verifica que el campo identification_number del modelo Patient
        rechace valores que no sean sólo dígitos lanzando ValidationError
        cuando se valida el campo o el modelo.
        """
        field = Patient._meta.get_field('identification_number')

        # validación directa del field
        with self.assertRaises(ValidationError):
            field.clean('ABC123', None)

        # validación al nivel del modelo (full_clean) — simula guardado
        p = Patient(identification_number='ABC123')
        with self.assertRaises(ValidationError):
            p.full_clean()