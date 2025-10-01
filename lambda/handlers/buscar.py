def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

from services.biblioteca_service import search_books

def handle(event,state):
    termino=_slot(event,'titulo')
    if not termino: return 'Dime el título a buscar.','¿Qué título buscas?'
    res=search_books(state,termino)
    if not res: return 'No encontré coincidencias.','¿Quieres buscar otro título?'
    texto=', '.join(l.get('titulo','(sin título)') for l in res[:10])
    return f'Encontré: {texto}.','¿Algo más?'
