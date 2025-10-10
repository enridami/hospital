from django import forms
from users.models import Consultation, Specialty

class ConsultationAttendForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = [
            'description', 'consultorio', 'servicio', 'temperatura', 'presion_sistolica', 'presion_diastolica',
            'frecuencia_respiratoria', 'pulso', 'saturacion_oxigeno', 'peso', 'talla', 'circunferencia_abdominal',
            'historia_actual', 'evolucion', 'impresion_diagnostica', 'hba1c', 'indicaciones'
        ]
        widgets = {
            'servicio': forms.Select(),
            'description': forms.Textarea(attrs={'readonly': True}),
        }

    def clean(self):
        cleaned_data = super().clean()
        required_fields = [
            'consultorio', 'servicio', 'temperatura', 'presion_sistolica', 'presion_diastolica',
            'frecuencia_respiratoria', 'pulso', 'saturacion_oxigeno', 'peso', 'talla'
        ]
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, "Este campo es obligatorio.")
        # Ejemplo de validación personalizada
        temp = cleaned_data.get('temperatura')
        if temp is not None and (temp < 30 or temp > 45):
            self.add_error('temperatura', "La temperatura debe estar entre 30 y 45 °C.")