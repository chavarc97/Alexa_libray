def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

def handle(_event,state):
    n=len(state['prestamos'])
    if n==0: return 'No hay préstamos activos.','¿Quieres prestar un libro?'
    return f'Tienes {n} préstamos activos.','¿Algo más?'
