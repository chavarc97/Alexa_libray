def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

def handle(_event,state):
    state['libros'].clear(); state['prestamos'].clear(); state['devueltos'].clear()
    return 'Listo, limpié tus datos.','¿Quieres agregar un libro ahora?'
