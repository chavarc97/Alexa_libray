def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

from services.biblioteca_service import return_book

def handle(event,state):
    libro=_slot(event,'id_libro') or _slot(event,'titulo')
    if not libro: return 'Dime el id o título del libro a devolver.','¿Cuál es?'
    ok,info=return_book(state,libro)
    if not ok and info=='no_encontrado': return 'No encontré ese libro.','¿Intentamos con otro?'
    if not ok and info=='no_prestado': return 'Ese libro no estaba prestado.','¿Quieres devolver otro?'
    return 'Gracias, quedó devuelto.','¿Algo más?'
