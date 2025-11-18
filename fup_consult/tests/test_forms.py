"""
Unit tests for RUC validation form.
"""

import pytest
from django import forms

from fup_consult.forms import RUCSearchForm


@pytest.mark.unit
class TestRUCSearchForm:
    """Test suite for RUC search form validation."""

    def test_valid_ruc_11_digits(self) -> None:
        """Test that a valid 11-digit RUC passes validation."""
        form = RUCSearchForm(data={"ruc": "20508238143"})
        assert form.is_valid()
        assert form.cleaned_data["ruc"] == "20508238143"

    def test_ruc_with_leading_zeros(self) -> None:
        """Test that RUC with leading zeros is valid."""
        form = RUCSearchForm(data={"ruc": "00123456789"})
        assert form.is_valid()

    def test_ruc_too_short(self) -> None:
        """Test that RUC with less than 11 digits is invalid."""
        form = RUCSearchForm(data={"ruc": "2050823814"})
        assert not form.is_valid()
        assert "ruc" in form.errors
        # Django min_length validation message
        error_text = str(form.errors["ruc"]).lower()
        assert "11" in error_text and ("carácter" in error_text or "dígitos" in error_text)

    def test_ruc_too_long(self) -> None:
        """Test that RUC with more than 11 digits is invalid."""
        form = RUCSearchForm(data={"ruc": "205082381433"})
        assert not form.is_valid()
        assert "ruc" in form.errors

    def test_ruc_with_letters(self) -> None:
        """Test that RUC with letters is invalid."""
        form = RUCSearchForm(data={"ruc": "2050823814A"})
        assert not form.is_valid()
        assert "ruc" in form.errors
        error_text = str(form.errors["ruc"]).lower()
        assert "número" in error_text or "dígito" in error_text

    def test_ruc_with_spaces(self) -> None:
        """Test that RUC with spaces is invalid."""
        form = RUCSearchForm(data={"ruc": "20508 238143"})
        assert not form.is_valid()
        assert "ruc" in form.errors

    def test_ruc_with_special_characters(self) -> None:
        """Test that RUC with special characters is invalid."""
        form = RUCSearchForm(data={"ruc": "20508238-143"})
        assert not form.is_valid()
        assert "ruc" in form.errors

    def test_empty_ruc(self) -> None:
        """Test that empty RUC is invalid."""
        form = RUCSearchForm(data={"ruc": ""})
        assert not form.is_valid()
        assert "ruc" in form.errors

    def test_ruc_field_required(self) -> None:
        """Test that RUC field is required."""
        form = RUCSearchForm(data={})
        assert not form.is_valid()
        assert "ruc" in form.errors

    def test_ruc_stripped_whitespace(self) -> None:
        """Test that whitespace is stripped from RUC."""
        form = RUCSearchForm(data={"ruc": " 20508238143 "})
        assert form.is_valid()
        assert form.cleaned_data["ruc"] == "20508238143"
