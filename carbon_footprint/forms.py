from django import forms
from .models import RideRecord


from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full p-2 border rounded mb-2',
        'placeholder': 'Email Address'
    }))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full p-2 border rounded mb-2',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full p-2 border rounded mb-2',
        'placeholder': 'Last Name'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded mb-2',
                'placeholder': 'Username'
            })
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full p-2 border rounded mb-2',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full p-2 border rounded mb-2',
        'placeholder': 'Password'
    }))


from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import RideRecord

class RideRecordForm(forms.ModelForm):
    class Meta:
        model = RideRecord
        fields = [
            'distance', 
            'fuel_type', 
            'num_riders', 
            'traffic_condition', 
            'idle_time',
            'ride_time'  # Add ride time to capture nighttime efficiency
        ]
        widgets = {
            'distance': forms.NumberInput(attrs={
                'class': 'w-full p-2 border rounded',
                'placeholder': 'Trip Distance (km)',
                'min': 0.1,
                'step': 0.1
            }),
            'fuel_type': forms.Select(attrs={
                'class': 'w-full p-2 border rounded',
                'help_text': 'Select vehicle fuel type'
            }),
            'num_riders': forms.NumberInput(attrs={
                'class': 'w-full p-2 border rounded', 
                'min': 1,
                'max': 8,  # Reasonable max passengers
                'placeholder': 'Number of Passengers'
            }),
            'traffic_condition': forms.Select(attrs={
                'class': 'w-full p-2 border rounded',
                'help_text': 'Current traffic conditions'
            }),
            'idle_time': forms.NumberInput(attrs={
                'class': 'w-full p-2 border rounded', 
                'min': 0,
                'max': 120,  # Reasonable max idle time
                'placeholder': 'Idle Time (minutes)'
            }),
            'ride_time': forms.DateTimeInput(attrs={
                'class': 'w-full p-2 border rounded',
                'type': 'datetime-local'
            })
        }
    
    # Comprehensive field validations
    def clean_distance(self):
        distance = self.cleaned_data.get('distance')
        if distance <= 0:
            raise forms.ValidationError("Distance must be greater than zero.")
        if distance > 1000:  # Reasonable max trip distance
            raise forms.ValidationError("Distance seems unrealistically large.")
        return distance
    
    def clean_num_riders(self):
        num_riders = self.cleaned_data.get('num_riders')
        if num_riders < 1:
            raise forms.ValidationError("At least one rider is required.")
        if num_riders > 8:
            raise forms.ValidationError("Maximum 8 passengers allowed.")
        return num_riders
    
    def clean_idle_time(self):
        idle_time = self.cleaned_data.get('idle_time')
        if idle_time < 0:
            raise forms.ValidationError("Idle time cannot be negative.")
        if idle_time > 120:
            raise forms.ValidationError("Idle time seems unrealistically long.")
        return idle_time
    
    def clean(self):
        """
        Additional cross-field validations
        """
        cleaned_data = super().clean()
        
        # Check fuel type specific constraints
        fuel_type = cleaned_data.get('fuel_type')
        distance = cleaned_data.get('distance')
        
        # Special validations for different vehicle types
        if fuel_type == 'ev':
            # Additional checks for electric vehicles
            if distance > 500:  # Assuming max EV range
                self.add_error('distance', "Distance exceeds typical EV range.")
        
        if fuel_type == 'diesel':
            # Diesel-specific considerations
            if distance > 800:  # Typical diesel vehicle range
                self.add_error('distance', "Distance exceeds typical diesel vehicle range.")
        
        return cleaned_data

    def get_dynamic_help_texts(self):
        """
        Dynamic help texts based on selected options
        """
        help_texts = {
            'fuel_type': {
                'petrol': 'Standard petrol vehicle with base emissions',
                'diesel': 'Diesel vehicles have 15% higher emissions',
                'ev': 'Electric vehicles have zero direct emissions'
            },
            'traffic_condition': {
                'light': 'No additional emissions adjustment',
                'moderate': '10% increase in emissions',
                'heavy': '20% increase in emissions'
            }
        }
        return help_texts

