def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

def handle(_event,_state):
    return 'De acuerdo. ¿Qué más deseas hacer?','¿Agregar, listar o eliminar libros?'
