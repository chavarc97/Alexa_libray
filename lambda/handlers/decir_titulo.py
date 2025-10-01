def _slot(event, name):
    try: return event['request']['intent']['slots'][name]['value']
    except Exception: return None

from services.biblioteca_service import add_book, delete_book

def handle(event, state):
    titulo = _slot(event, 'titulo')
    if not titulo:
        return 'No escuché el título.','¿Cuál es el título?'

    # Flujo 1: venimos de "agregar"
    if state.get('__await__') == 'titulo':
        ok, info = add_book(state, titulo, None, None)
        state.pop('__await__', None)
        if not ok and info == 'duplicado':
            return f"'{titulo}' ya existe. ¿Agregamos otro?", 'Dime otro título.'
        return f"Listo, agregué '{titulo}'.", '¿Quieres hacer algo más?'

    # Flujo 2: venimos de "eliminar"
    if state.get('__await__') == 'eliminar':
        ok, info = delete_book(state, titulo, None)
        state.pop('__await__', None)
        if not ok and info == 'no_encontrado':
            return f"No encontré un libro que coincida con {titulo}.", 'Dime otro título.'
        if not ok and info == 'prestado':
            return 'Ese libro está prestado; primero debe devolverse.', '¿Eliminar otro libro?'
        t = info.get('titulo','el libro')
        return f"Listo, eliminé {t}.", '¿Algo más?'

    # Sin contexto previo
    return f"Tomé el título '{titulo}'. Puedes decir: agregar para guardarlo o eliminar para borrarlo.", '¿Qué deseas hacer?'
