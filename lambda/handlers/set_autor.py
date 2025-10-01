# lambda/handlers/set_autor.py

def _slot(event, name):
    intent = (event.get("request") or {}).get("intent") or {}
    slot = (intent.get("slots") or {}).get(name) or {}
    val = slot.get("value")
    return val.strip() if isinstance(val, str) and val.strip() else None

def handle(event, state):
    autor = _slot(event, "autor")
    libros = state.setdefault("libros", [])

    if not autor:
        return ("Necesito el nombre del autor. Puedes decir: el autor es Gabriel Garcia Marquez.",
                "Dime el nombre del autor, por favor.")

    if not libros:
        return ("Aun no tienes libros guardados. Primero agrega un libro con su genero.",
                "Puedes decir: agrega Dune de genero ciencia ficcion.")

    # Estrategia simple: asignar al ultimo libro agregado
    libro = libros[-1]
    libro["autor"] = autor

    titulo = libro.get("titulo", "sin titulo")
    genero = libro.get("tipo", "sin genero")

    speak = (f"Listo. Asigne el autor {autor} a “{titulo}” ({genero}). "
             "¿Quieres agregar otro libro o listar tus libros?")
    reprompt = "Puedes decir: agregar otro libro o listar mis libros."
    return (speak, reprompt)
