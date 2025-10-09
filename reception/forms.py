from django import forms
from users.models import Patient, Consultation

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'identification_type', 'identification_number',
            'gender', 'date_of_birth', 'address_line', 'city',
            'region', 'postal_code', 'country', 'blood_type',
            'allergies', 'medical_notes', 'emergency_contact_name',
            'emergency_contact_relationship', 'emergency_contact_phone',
            'assigned_doctor', 'is_active'
        ]

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = [
            'description', 'date', 'time', 'shift',
            'priority', 'status', 'doctor', 'patient'
        ]