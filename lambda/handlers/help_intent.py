def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

# lambda/handlers/help_intent.py
def handle(event, state):
    speak = ("Puedo agregar, listar, buscar, prestar, devolver y eliminar libros. "
             "Por ejemplo: agrega Dune de genero ciencia ficcion, lista mis libros "
             "o presta Dune a Juan. ¿Qué te gustaría hacer?")
    reprompt = "Di: agrega un libro; o: lista mis libros."
    return (speak, reprompt)
