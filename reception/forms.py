from django import forms
from users.models import Patient, Consultation

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
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha"
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Hora"
    )
    class Meta:
        model = Consultation
        fields = [
            'description', 'date', 'time', 'shift',
            'priority', 'status', 'doctor', 'patient'
        ]