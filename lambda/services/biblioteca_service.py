from typing import Dict, Any, List, Optional, Tuple, Union
from shared.utils import norm

# Tipos seguros para 3.7
Book = Dict[str, Any]
Result = Tuple[bool, Union[str, Book]]

def _next_id(state: Dict[str, Any]) -> str:
    return str(len(state["libros"]) + 1)

def add_book(state: Dict[str, Any], titulo: str, autor: Optional[str], tipo: Optional[str]) -> Result:
    t = norm(titulo)
    for l in state["libros"]:
        if norm(l.get("titulo")) == t:
            return False, "duplicado"
    libro = {"id": _next_id(state), "titulo": titulo, "autor": autor or "Desconocido",
             "tipo": tipo or "General", "estado": "disponible"}
    state["libros"].append(libro)
    return True, libro

def list_books(state: Dict[str, Any]) -> List[Book]:
    return state["libros"]

def search_books(state: Dict[str, Any], termino: str) -> List[Book]:
    t = norm(termino)
    return [l for l in state["libros"] if t in norm(l.get("titulo"))]

def delete_book(state: Dict[str, Any], titulo: Optional[str], libro_id: Optional[str]) -> Result:
    libros = state["libros"]
    idx, obj = -1, None
    if libro_id:
        for i,l in enumerate(libros):
            if str(l.get("id")) == str(libro_id):
                idx, obj = i, l; break
    elif titulo:
        t = norm(titulo)
        for i,l in enumerate(libros):
            if t in norm(l.get('titulo')) or norm(l.get('titulo')) in t:
                idx, obj = i, l; break
    if idx == -1:
        return False, "no_encontrado"
    for p in state["prestamos"]:
        if p.get("libro_id") == obj.get("id"):
            return False, "prestado"
    libros.pop(idx)
    return True, obj

def borrow_book(state: Dict[str, Any], libro_or_title: str, persona: Optional[str]) -> Tuple[bool, str]:
    t = norm(libro_or_title)
    libro = next((l for l in state["libros"] if str(l.get("id"))==libro_or_title or norm(l.get("titulo"))==t), None)
    if not libro: return False, "no_encontrado"
    if any(p.get("libro_id")==libro["id"] for p in state["prestamos"]): return False, "prestado"
    state["prestamos"].append({"libro_id": libro["id"], "a": persona or "alguien"})
    libro["estado"]="prestado"
    return True, "ok"

def return_book(state: Dict[str, Any], libro_or_title: str) -> Tuple[bool, str]:
    t = norm(libro_or_title)
    libro = next((l for l in state["libros"] if str(l.get("id"))==libro_or_title or norm(l.get("titulo"))==t), None)
    if not libro: return False, "no_encontrado"
    i = next((i for i,p in enumerate(state["prestamos"]) if p.get("libro_id")==libro["id"]), -1)
    if i == -1: return False, "no_prestado"
    state["devueltos"].append(state["prestamos"].pop(i))
    libro["estado"]="disponible"
    return True, "ok"
