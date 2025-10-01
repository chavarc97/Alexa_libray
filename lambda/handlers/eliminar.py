# lambda/handlers/eliminar.py
import unicodedata

def _intent(event):
    return (event.get("request") or {}).get("intent") or {}

def _slot(intent, name):
    s = (intent.get("slots") or {}).get(name) or {}
    v = s.get("value")
    return v.strip() if isinstance(v, str) and v.strip() else None

def _normalize(s):
    # quita acentos, pasa a minúsculas y compacta espacios
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return " ".join(s.lower().split())

def _elicit(slot_to_elicit, speech, reprompt=None, intent=None):
    d = {"type": "Dialog.ElicitSlot", "slotToElicit": slot_to_elicit}
    if intent:
        d["updatedIntent"] = intent
    return {"speak": speech, "reprompt": reprompt or speech, "directives": [d], "end": False}

def _find_book_idx(libros, titulo_usuario):
    """Busca por coincidencia flexible: exacto, empieza con, contiene."""
    if not titulo_usuario:
        return -1
    key = _normalize(titulo_usuario)

    # primero exacto
    for i, b in enumerate(libros):
        if _normalize(b.get("titulo", "")) == key:
            return i
    # luego startswith
    for i, b in enumerate(libros):
        if _normalize(b.get("titulo", "")).startswith(key):
            return i
    # luego contains
    for i, b in enumerate(libros):
        if key in _normalize(b.get("titulo", "")):
            return i
    return -1

def handle(event, state):
    intent = _intent(event)
    titulo = _slot(intent, "titulo")

    libros = state.setdefault("libros", [])

    # Si no hay libros todavía
    if not libros:
        return (
            "Aún no tienes libros guardados. Primero agrega uno.",
            "Puedes decir: agrega Dune de genero ciencia ficcion."
        )

    # Si no vino el título: elicita con ayuda contextual
    if not titulo:
        # arma una vista rápida de hasta 5 títulos
        ejemplos = ", ".join(b.get("titulo", "sin titulo") for b in libros[:5]) or "ninguno"
        speak = (f"Claro. Dime el título del libro que quieres eliminar. "
                 f"Por ejemplo: {ejemplos}.")
        reprompt = "Dime el título, por ejemplo: Dune."
        return _elicit("titulo", speak, reprompt, intent)

    # Buscar el libro
    idx = _find_book_idx(libros, titulo)
    if idx == -1:
        speak = (f"No encontré “{titulo}”. Si quieres, puedo listar tus libros para que elijas.")
        reprompt = "Di: lista mis libros. O vuelve a decir el título a eliminar."
        return (speak, reprompt)

    # Eliminar y confirmar
    libro = libros.pop(idx)
    titulo_ok = libro.get("titulo", titulo)
    genero_ok = libro.get("tipo", None)
    autor_ok  = libro.get("autor", None)

    detalle = []
    if genero_ok: detalle.append(genero_ok)
    if autor_ok:  detalle.append(f"autor {autor_ok}")
    det = f" ({', '.join(detalle)})" if detalle else ""

    speak = (f"Listo. Eliminé “{titulo_ok}”{det} de tu biblioteca. "
             "¿Quieres eliminar otro, agregar un libro nuevo o listar tus libros?")
    reprompt = "Puedes decir: eliminar otro, agregar un libro o listar mis libros."
    return (speak, reprompt)
