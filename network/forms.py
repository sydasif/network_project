# forms.py
from django import forms

TASK_CHOICES = [
    ("show_ip", "Show IP Interface Brief"),
    ("save_config", "Save Running Config"),
    ("get_device_uptime", "Get Device Uptime"),
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
