# myapp/utils.py
from decimal import Decimal, InvalidOperation

def safe_decimal(value, default=0):
    """Convert a string or number to Decimal safely."""
    try:
        return Decimal(value)
    except (TypeError, InvalidOperation):
        return Decimal(default)