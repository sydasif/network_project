# forms.py
from django import forms

from .models import NetworkDevice

TASK_CHOICES = [
    ("show_ip", "Show IP Interface Brief"),
    ("save_config", "Save Running Config"),
]


class TaskForm(forms.Form):
    task_type = forms.ChoiceField(choices=TASK_CHOICES)
    devices = forms.MultipleChoiceField(
        choices=[],  # Filled in the view dynamically
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        device_choices = kwargs.pop("device_choices", [])
        super().__init__(*args, **kwargs)
        self.fields["devices"].choices = device_choices


class DeviceForm(forms.ModelForm):
    class Meta:
        model = NetworkDevice
        fields = ["hostname", "name"]
        widgets = {
            "password": forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                }
            )
