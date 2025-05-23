# forms.py
from django import forms

from .models import NetworkDevice, TaskLog

STATUS_CHOICES = [
    ("", "---------"),  # Optional: Add an empty choice for no status filter
    ("success", "Success"),
    ("failure", "Failure"),
]

TASK_CHOICES = [
    ("show_ip", "Show IP Interface Brief"),
    ("save_config", "Save Running Config"),
    ("custom_command", "Run Custom Command"),
]


class TaskForm(forms.Form):
    task_type = forms.ChoiceField(choices=TASK_CHOICES)
    custom_command = forms.CharField(
        widget=forms.Textarea, required=False, label="Custom Command"
    )
    devices = forms.MultipleChoiceField(
        choices=[],  # Filled in the view dynamically
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        device_choices = kwargs.pop("device_choices", [])
        super().__init__(*args, **kwargs)
        self.fields["devices"].choices = device_choices


class TaskLogFilterForm(forms.Form):
    device_name = forms.ChoiceField(choices=[], required=False)
    task_type = forms.ChoiceField(choices=[], required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate device_name choices
        device_names = (
            TaskLog.objects.all().values_list("device_name", flat=True).distinct()
        )
        self.fields["device_name"].choices = [("", "---------")] + [
            (name, name) for name in device_names
        ]

        # Dynamically populate task_type choices
        task_types = (
            TaskLog.objects.all().values_list("task_type", flat=True).distinct()
        )
        self.fields["task_type"].choices = [("", "---------")] + [
            (type, type) for type in task_types
        ]


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
