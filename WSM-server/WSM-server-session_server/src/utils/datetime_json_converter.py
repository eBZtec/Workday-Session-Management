from datetime import datetime


def datetime_json_converter(obj):
    """Converte objetos não serializáveis como datetime para strings."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj