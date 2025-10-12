from django import forms
from users.models import Patient, Consultation, Doctor

class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de Nacimiento"
    )
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'identification_type', 'identification_number',
            'gender', 'date_of_birth', 'address_line', 'city',
            'region', 'postal_code', 'country', 'blood_type',
            'allergies', 'medical_notes', 'emergency_contact_name',
            'emergency_contact_relationship', 'emergency_contact_phone'
        ]

class ConsultationForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha"
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Hora"
    )

    class Meta:
        model = Consultation
        fields = ['doctor', 'date', 'time', 'shift', 'status', 'description']
        # No incluyas 'patient' aquí, lo asignas desde la vista

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Puedes personalizar widgets aquí si lo necesitas
        self.fields['doctor'].queryset = Doctor.objects.none()

    # Validar que el paciente esté presente si es nuevo, si el paciente no esta se muestra un error general en el formulario
    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk and not getattr(self.instance, 'patient', None):
            raise forms.ValidationError("Debes seleccionar un paciente antes de agendar la consulta.")
        return cleaned_data