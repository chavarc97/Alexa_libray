def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

# lambda/handlers/fallback_intent.py
def handle(event, state):
    speak = ("Creo que no te entendí. Puedo agregar, listar, buscar, prestar, "
             "devolver y eliminar libros. Por ejemplo: agrega Dune de genero ciencia ficcion "
             "o lista mis libros. ¿Qué hacemos?")
    reprompt = "Intenta con: agrega un libro; o: listar mis libros."
    return (speak, reprompt)
