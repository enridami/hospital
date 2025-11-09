from django import forms
from users.models import Patient, Consultation, Doctor, DoctorSchedule

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
    # El campo consultorio ya no se incluye aquí

    class Meta:
        model = Consultation
        fields = ['doctor', 'date', 'time', 'shift', 'status', 'description']  # consultorio excluido

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        # consultorio se obtiene en la vista, no del formulario

        if not self.instance.pk and not getattr(self.instance, 'patient', None):
            raise forms.ValidationError("Debes seleccionar un paciente antes de agendar la consulta.")

        # La validación de consultorio se debe hacer en la vista, no aquí
        return cleaned_data