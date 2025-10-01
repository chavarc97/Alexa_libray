# lambda/handlers/agregar.py

# ====== Configuración de géneros conocidos ======
GENS = [
    "ciencia ficcion", "fantasia", "misterio", "terror", "romance",
    "aventura", "historia", "realismo magico", "novela grafica"
]

# Palabras que suelen venir al principio del título cuando el usuario da "comandos"
STOPWORDS_INICIO = ["agrega", "agregar", "añade", "añadir", "registra", "el libro", "libro"]
# Conectores que a veces quedan colgando al final
STOPWORDS_MEDIO  = ["de", "del"]

# ====== Utilidades de intent/slots/dialog ======
def _intent(event):
    return (event.get("request") or {}).get("intent") or {}

def _get_intent(event):
    # alias de _intent para compatibilidad
    return _intent(event)

def _slot(intent, name):
    slot = (intent.get("slots") or {}).get(name) or {}
    val = slot.get("value")
    return val.strip() if isinstance(val, str) and val.strip() else None

def _dialog_state(event):
    return (event.get("request") or {}).get("dialogState")

def _set_slot(intent, name, value):
    """Escribe un slot en el intent (para updatedIntent)."""
    slots = intent.setdefault("slots", {})
    s = slots.setdefault(name, {"name": name, "confirmationStatus": "NONE"})
    s["name"] = name
    s["value"] = value
    s["confirmationStatus"] = s.get("confirmationStatus", "NONE")

def _delegate(intent=None):
    d = {"type": "Dialog.Delegate"}
    if intent:
        d["updatedIntent"] = intent
    return d

def _delegate_with_updated_intent(intent, speak=None, reprompt=None):
    d = {"type": "Dialog.Delegate", "updatedIntent": intent}
    return {
        "speak": speak or "Entendido.",
        "reprompt": reprompt or "Continuemos.",
        "directives": [d],
        "end": False,
    }

def _elicit(slot_to_elicit, speech, reprompt=None, intent=None):
    d = {"type": "Dialog.ElicitSlot", "slotToElicit": slot_to_elicit}
    if intent:
        d["updatedIntent"] = intent
    return {"speak": speech, "reprompt": reprompt or speech, "directives": [d], "end": False}

# ====== Utilidades de normalización/parsing de frase ======
def _normalize(s):
    return " ".join(s.strip().split())

def _strip_leading_tokens(text):
    t = text.strip()
    low = t.lower()
    # elimina repetidamente tokens de inicio
    changed = True
    while changed:
        changed = False
        for w in STOPWORDS_INICIO:
            wl = w.lower()
            if low.startswith(wl + " "):
                t = t[len(w):].lstrip()
                low = t.lower()
                changed = True
    return t

def _remove_trailing_connectors(t):
    low = t.lower().rstrip()
    for w in STOPWORDS_MEDIO:
        if low.endswith(" " + w):
            low = low[:-(len(w)+1)].rstrip()
    return low

def _extract_genre_from_phrase(phrase):
    """
    Intenta separar 'titulo' y 'genero' de frases como:
    'agrega dune de genero ciencia ficcion', 'dune genero terror', 'dune del genero fantasia'
    Devuelve (titulo_limpio | None, genero | None).
    """
    if not phrase:
        return None, None
    p = phrase.strip()
    pl = p.lower().replace("género", "genero")

    # Detecta 'genero X' en la frase
    for g in GENS:
        key = f"genero {g}"
        if key in pl:
            left = pl.split(key)[0]
            # Limpia conectores: 'de genero', 'del genero'
            left = left.replace("de genero", "").replace("del genero", "")
            # Quita verbos de comando al inicio y conectores al final
            left = _strip_leading_tokens(left)
            left = _remove_trailing_connectors(left)
            titulo = _normalize(left) or None
            return titulo, g

    # Detecta si termina exactamente en un genero conocido
    for g in GENS:
        if pl.endswith(g):
            # Busca conectores comunes antes del genero
            for key in [" de genero ", " del genero ", " genero "]:
                if key in pl:
                    left = pl.rsplit(key, 1)[0]
                    left = _strip_leading_tokens(left)
                    left = _remove_trailing_connectors(left)
                    titulo = _normalize(left) or None
                    return titulo, g

    return phrase, None

# ====== Handler principal ======
def handle(event, state):
    """
    Flujo:
    1) Si el usuario dice título + género en una misma frase (cae en 'titulo' porque es SearchQuery),
       intentamos extraer el género y prellenar los slots en updatedIntent.
    2) Mientras falten 'titulo' o 'tipo', usamos dialog (Delegate/Elicit) con mensajes naturales.
    3) Cuando esté COMPLETED, guardamos y confirmamos.
    """
    intent_obj = _get_intent(event)
    dialog_state = _dialog_state(event)

    titulo = _slot(intent_obj, "titulo")
    genero = _slot(intent_obj, "tipo")    # tipo = género (custom slot GENERO_LIBRO)
    autor  = _slot(intent_obj, "autor")   # opcional

    # 1) Si llegó todo en 'titulo', intenta extraer 'genero'
    if titulo and not genero:
        maybe_title, maybe_genre = _extract_genre_from_phrase(titulo)
        if maybe_genre in GENS:
            # Pre-llenamos los slots en el intent y delegamos
            _set_slot(intent_obj, "titulo", (maybe_title or titulo))
            _set_slot(intent_obj, "tipo",   maybe_genre)
            return _delegate_with_updated_intent(
                intent_obj,
                speak="Perfecto, lo registré como ciencia ficcion.",
                reprompt="¿Continuamos?"
            )

    # 2) Dialog Management: pedir lo que falte con guía clara
    if dialog_state != "COMPLETED":
        if not titulo and not genero:
            return {
                "speak": ("Perfecto. Para registrarlo bien, dime el titulo y el genero. "
                          "Por ejemplo di agrega Dune y cuando te pregunte di ciencia ficcion."),
                "reprompt": "Dime primero el titulo y luego el genero.",
                "directives": [_delegate(intent_obj)]
            }

        if not titulo:
            return _elicit(
                "titulo",
                "De acuerdo. ¿Cual es el titulo del libro? Puedes decir Se llama Dune.",
                "Dime el titulo exacto del libro.",
                intent_obj
            )

        if not genero:
            return _elicit(
                "tipo",
                "Ahora, ¿de que genero es? Por ejemplo ciencia ficcion fantasia misterio o terror.",
                "¿Que genero es?",
                intent_obj
            )

        # Seguridad: si algo se escapó, delega
        return {"directives": [_delegate(intent_obj)], "speak": "Entendido.", "reprompt": "Continuemos."}

    # 3) Aquí ya están completos los slots requeridos (o quedaron prellenados)
    titulo = (titulo or "sin titulo").strip()
    genero = (genero or "sin genero").strip()

    # Guarda en tu estado (si tienes DB real, reemplaza esto por tu helper)
    libros = state.setdefault("libros", [])
    libros.append({"titulo": titulo, "tipo": genero, "autor": autor})

    # Respuesta natural y siguiente acción sugerida
    if autor:
        speak = (f"¡Listo! Agregue “{titulo}” como {genero} y autor {autor}. "
                 "¿Quieres agregar otro libro o prefieres listar tus libros?")
    else:
        speak = (f"Hecho. Agregue “{titulo}” como {genero}. "
                 "Si quieres tambien puedo guardar el autor. "
                 "Di por ejemplo agrega el autor Frank Herbert. "
                 "¿Agregamos otro libro o listamos tus libros?")

    reprompt = "Puedes decir agregar otro libro, listar mis libros o buscar Dune."
    return {"speak": speak, "reprompt": reprompt, "end": False}
