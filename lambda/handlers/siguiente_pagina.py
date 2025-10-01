def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

def handle(_event,_state):
    return 'Por ahora no hay más páginas.','¿Deseas otra cosa?'
