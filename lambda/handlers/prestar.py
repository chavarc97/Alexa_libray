def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

from services.biblioteca_service import borrow_book

def handle(event,state):
    libro=_slot(event,'id_libro') or _slot(event,'titulo'); persona=_slot(event,'persona')
    if not libro: return 'Dime el id o título del libro a prestar.','¿Cuál es?'
    ok,info=borrow_book(state,libro,persona)
    if not ok and info=='no_encontrado': return 'No encontré ese libro.','¿Intentamos con otro?'
    if not ok and info=='prestado': return 'Ese libro ya está prestado.','¿Quieres prestar otro?'
    return 'Listo, quedó prestado.','¿Algo más?'
