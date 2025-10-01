def get_state(event):
    attrs = (event.get("session") or {}).get("attributes") or {}
    attrs.setdefault("libros", [])
    attrs.setdefault("prestamos", [])
    attrs.setdefault("devueltos", [])
    return attrs
