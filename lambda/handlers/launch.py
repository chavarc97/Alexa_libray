def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

def handle(_event,_state):
    return '¡Bienvenido! ¿Qué deseas hacer?','Puedes decir: agregar el libro El Principito.'
