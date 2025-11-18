"""
Forms for RUC validation.
"""

from django import forms


class RUCSearchForm(forms.Form):
    """Form for searching provider by RUC."""

    ruc = forms.CharField(
        max_length=11,
        min_length=11,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Ingrese RUC de 11 dígitos",
                "pattern": "[0-9]{11}",
                "title": "Ingrese exactamente 11 dígitos numéricos",
            }
        ),
        label="RUC",
        help_text="Ingrese el número de RUC de 11 dígitos",
    )

    def clean_ruc(self) -> str:
        """Validate and clean RUC field."""
        ruc = self.cleaned_data.get("ruc", "").strip()

        if not ruc:
            raise forms.ValidationError("El RUC es obligatorio.")

        if len(ruc) != 11:
            raise forms.ValidationError("El RUC debe tener exactamente 11 dígitos.")

        if not ruc.isdigit():
            raise forms.ValidationError("El RUC solo debe contener números.")

        return ruc
