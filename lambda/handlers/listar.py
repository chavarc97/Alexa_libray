def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

from services.biblioteca_service import list_books

# lambda/handlers/listar.py
def handle(event, state):
    libros = state.get("libros") or []
    if not libros:
        return ("No tienes libros guardados aún. ¿Quieres agregar uno?",
                "Di: agrega Dune de genero ciencia ficcion.")
    # arma listado breve
    titulos = [b.get("titulo","sin titulo") for b in libros]
    listado = ", ".join(titulos[:10])
    extra = "" if len(titulos) <= 10 else f" y {len(titulos)-10} más"
    speak = f"Tus libros: {listado}{extra}. ¿Quieres buscar, eliminar alguno o agregar uno nuevo?"
    reprompt = "Puedes decir: buscar Dune, eliminar El Hobbit o agregar un libro."
    return (speak, reprompt)
