def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

def handle(_event,state):
    n=len(state['devueltos'])
    if n==0: return 'No hay devoluciones registradas.','¿Algo más?'
    return f'Tienes {n} devoluciones registradas.','¿Algo más?'
