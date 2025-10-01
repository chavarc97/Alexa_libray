import importlib, sys, os
import json
import traceback

# Asegura que /lambda esté en el path
_runtime_dir = os.path.dirname(__file__)
if _runtime_dir not in sys.path:
    sys.path.insert(0, _runtime_dir)

def _say(text, reprompt=None, end=False, session=None, directives=None):
    r = {
        "version": "1.0",
        "sessionAttributes": session or {},
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text or ""},
            "shouldEndSession": bool(end),
        },
    }
    if reprompt:
        r["response"]["reprompt"] = {
            "outputSpeech": {"type": "PlainText", "text": reprompt}
        }
        # Si hay reprompt, la sesión NO debe terminar
        r["response"]["shouldEndSession"] = False
    if directives:
        r["response"]["directives"] = directives
        # Si mandas Dialog.* directives, la sesión NO debe terminar
        r["response"]["shouldEndSession"] = False
    return r


_ROUTES = {
    "MostrarOpcionesIntent": "mostrar_opciones",
    "ContinuarAgregarIntent": "continuar_agregar",
    "AgregarLibroIntent": "agregar",
    "AgregarAutorIntent": "set_autor",          
    "EliminarLibroIntent": "eliminar",
    "ListarLibrosIntent": "listar",
    "BuscarLibroIntent": "buscar",
    "PrestarLibroIntent": "prestar",
    "DevolverLibroIntent": "devolver",
    "ConsultarPrestamosIntent": "consultar_prestamos",
    "ConsultarDevueltosIntent": "consultar_devueltos",
    "LimpiarCacheIntent": "limpiar_cache",
    "SiguientePaginaIntent": "siguiente_pagina",
    "SalirListadoIntent": "salir_listado",
    "AMAZON.HelpIntent": "help_intent",
    "AMAZON.CancelIntent": "stop_intent",
    "AMAZON.StopIntent": "stop_intent",
    "AMAZON.FallbackIntent": "fallback_intent",
}


def _say(text, reprompt=None, end=False, session=None, directives=None):
    r = {
        "version": "1.0",
        "sessionAttributes": session or {},
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": end,
        },
    }
    if reprompt:
        r["response"]["reprompt"] = {"outputSpeech": {"type": "PlainText", "text": reprompt}}
    if directives:  # <-- IMPORTANTE
        r["response"]["directives"] = directives  # <-- IMPORTANTE
    return r



def _load_handler(intent_name):
    mod_name = _ROUTES.get(intent_name, "fallback_intent")
    mod = importlib.import_module("handlers." + mod_name)
    return mod.handle

def _get_state(event):
    try:
        from helpers.database import get_state
        return get_state(event)
    except Exception:
        attrs = (event.get("session") or {}).get("attributes") or {}
        attrs.setdefault("libros", [])
        attrs.setdefault("prestamos", [])
        attrs.setdefault("devueltos", [])
        return attrs



def lambda_handler(event, context):
    try:
        req = event.get("request") or {}
        rtype = req.get("type")
        state = _get_state(event)

        if rtype == "LaunchRequest":
            return _say(
                "¡Hola! Puedo agregar, listar, buscar, prestar, devolver y eliminar libros. "
                "Por ejemplo: di agrega Dune de genero ciencia ficcion. ¿Qué te gustaría hacer?",
                "Puedes decir: agrega un libro; o: lista mis libros.",
                session=state,
            )

        if rtype == "IntentRequest":
            name = (req.get("intent") or {}).get("name") or "AMAZON.FallbackIntent"
            handler = _load_handler(name)
            result = handler(event, state)

            # Compatibilidad: (speak, reprompt) o dict enriquecido
            if isinstance(result, tuple):
                speak, reprompt = result
                return _say(speak, reprompt, session=state)
            elif isinstance(result, dict):
                return _say(
                    result.get("speak", "Listo."),
                    result.get("reprompt"),
                    end=result.get("end", False),
                    session=state,
                    directives=result.get("directives"),
                )
            else:
                return _say(
                    "No entendí la respuesta del manejador.",
                    "¿Intentamos de nuevo?",
                    session=state,
                )

        if rtype == "SessionEndedRequest":
            return _say("Hasta luego.", end=True, session=state)

        # Tipo inesperado
        return _say(
            "Ocurrió un problema con la solicitud.",
            "¿Intentamos de nuevo?",
            session=state,
        )

    except Exception as e:
        # Log detallado para CloudWatch
        print("### EXCEPTION ###")
        print(json.dumps(event, ensure_ascii=False))
        traceback.print_exc()

        # Respuesta mínima válida (sin llamar helpers que puedan fallar)
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {"type": "PlainText", "text": "Lo siento, tuve un problema interno."},
                "shouldEndSession": False,
            },
            "sessionAttributes": {},
        }
