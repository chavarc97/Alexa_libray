# Diseño de Software - Sistema de Gestión de Biblioteca Personal

**Versión:** 1.0

**Autor(es):** Equipo de Desarrollo

**Fecha:** 22 de Septiembre, 2025

**Historial de revisiones:**


| Versión | Fecha      | Autor(es) | Cambios Realizados              | Aprobado por      |
| -------- | ---------- | --------- | ------------------------------- | ----------------- |
| 0.1      | 2025-09-22 | Equipo    | Creación inicial del documento | Líder del equipo |
| .2       | 2025-09-27 | Equipo    | Diagramas C4 y de VUI           | Líder del equipo |

## 1. Introducción (Caso de uso)

### Descripción general del sistema

El proyecto consiste en una skill de Alexa llamada Manolito, que sirve para manejar una biblioteca personal de libros. El usuario puede hablar con Alexa para agregar, eliminar, listar, buscar, prestar y devolver libros, todo mediante comandos de voz. La información se guarda en la nube (Amazon S3).

### Objetivo del documento

Definir la arquitectura y diseño del sistema aplicando principios SOLID y los cuatro pilares de la POO, migrando desde una implementación monolítica hacia una estructura modular y mantenible.

### Alcance

**Incluye:**

* Gestión de inventario de libros (agregar, listar, buscar)
* Sistema de préstamos y devoluciones
* Persistencia de datos en S3
* Interfaz de voz natural con diálogos conversacionales
* Paginación de resultados
* Historial de transacciones
* Eliminación de libros (funcionalidad adicional)

**No incluye:**

* Gestión de usuarios múltiples
* Integración con servicios externos de libros
* Funciones de compra/venta

### Actores principales

* **Usuario primario:** Propietario de la biblioteca personal
* **Sistema Alexa:** Interfaz de interacción vocal
* **Amazon S3:** Servicio de persistencia de datos

### Casos de uso relevantes

1. Agregar libros mediante diálogo conversacional
2. Consultar inventario con paginación
3. Registrar préstamos con fechas límite
4. Procesar devoluciones
5. Consultar historial de movimientos
6. Eliminar libros de la colección

---

## 2. Problem Statement (Declaración del problema)

### Contexto

El código actual está implementado como un monolito en un único archivo `lambda_function.py` de más de 1000 líneas, donde toda la lógica de negocio, manejo de datos, y control de interfaz están mezclados sin separación de responsabilidades.

### Problemas específicos

* **Mantenibilidad:** Difícil de modificar y extender debido al acoplamiento alto
* **Testabilidad:** Imposible realizar pruebas unitarias efectivas
* **Escalabilidad:** Agregar nuevas funcionalidades requiere modificar múltiples secciones
* **Legibilidad:** Código complejo y difícil de entender
* **Reutilización:** Lógica duplicada en múltiples handlers

### Impacto de no resolverlos

* Tiempo de desarrollo incrementado exponencialmente
* Mayor probabilidad de bugs al hacer cambios
* Dificultad para onboarding de nuevos desarrolladores
* Imposibilidad de implementar CI/CD efectivo

### Restricciones del entorno

* Debe funcionar en AWS Lambda
* Compatibilidad con Alexa Skills Kit
* Límites de tiempo de ejecución de Lambda (15 minutos máx)
* Restricciones de memoria y almacenamiento temporal

---

## 3. Requerimientos funcionales


| ID    | Descripción                     | Actor   | Prioridad | Criterios de aceptación                                              |
| ----- | -------------------------------- | ------- | --------- | --------------------------------------------------------------------- |
| RF-01 | Agregar libros mediante diálogo | Usuario | Alta      | El sistema debe solicitar título, autor y tipo en pasos secuenciales |
| RF-02 | Listar libros con paginación    | Usuario | Alta      | Mostrar máximo 10 libros por página con navegación                 |
| RF-03 | Buscar libros por título/autor  | Usuario | Media     | Encontrar coincidencias parciales en títulos y autores               |
| RF-04 | Registrar préstamos             | Usuario | Alta      | Capturar libro, persona y fecha límite automática                   |
| RF-05 | Procesar devoluciones            | Usuario | Alta      | Actualizar estado y registrar en historial                            |
| RF-06 | Consultar préstamos activos     | Usuario | Media     | Mostrar libros prestados con fechas y personas                        |
| RF-07 | Ver historial completo           | Usuario | Baja      | Acceder a todas las transacciones pasadas                             |
| RF-08 | Eliminar libros                  | Usuario | Media     | Remover libros de la colección con confirmación                     |
| RF-09 | Sincronizar estados              | Sistema | Alta      | Mantener consistencia entre libros y préstamos                       |
| RF-10 | Persistir datos                  | Sistema | Alta      | Guardar/recuperar datos desde S3 automáticamente                     |

---

## 4. Requerimientos no funcionales


| ID     | Atributo       | Descripción                 | Métricas / criterios cuantitativos     |
| ------ | -------------- | ---------------------------- | --------------------------------------- |
| RNF-01 | Rendimiento    | Respuesta rápida en Lambda  | < 3 segundos por operación             |
| RNF-02 | Escalabilidad  | Soporte múltiples libros    | Hasta 1000 libros por usuario           |
| RNF-03 | Disponibilidad | Funcionamiento continuo      | 99.9% uptime                            |
| RNF-04 | Usabilidad     | Interacción natural por voz | Comprensión > 90% comandos válidos    |
| RNF-05 | Mantenibilidad | Código modular y testeable  | Cobertura de pruebas > 80%              |
| RNF-06 | Seguridad      | Datos de usuario protegidos  | Encriptación en S3, acceso por usuario |

---

## 5. Arquitectura / Diseño – C4 Diagrams

### Descripción general de la arquitectura

El sistema sigue una arquitectura por capas con separación clara de responsabilidades:

* **Capa de Presentación:** Handlers de Alexa
* **Capa de Lógica de Negocio:** Services y Controllers
* **Capa de Datos:** Repositories y Models
* **Capa de Infraestructura:** Adapters y Utilities

### Diagramas C4

#### Diagrama de Contexto (Level 1)

```mermaid
C4Context
title System Context diagram for Biblioteca Personal Skill

Person(user, "Usuario", "Usuario de la Biblioteca Personal Skill")
System_Boundary(alexa_boundary, "Amazon Alexa") {
  System(alexa, "Amazon Alexa", "Voice service platform")
  System(skill, "Biblioteca Personal Skill", "Alexa Skill for managing books")
  System(AWS Lambda, "Backend", "Logica de la skill")
}

SystemDb(s3, "Amazon S3", "Object Storage")


Rel(user, alexa, "Comandos de voz")
Rel(alexa, user, "Respuestas de voz")
Rel(user, alexa, "Uses")
Rel(alexa, skill, "Invokes Skill")
Rel(skill, AWS Lambda, "Invoca Lambda")
Rel(AWS Lambda, s3, "Uses")

```

#### Diagrama de Contenedores (Level 2)

```mermaid
C4Container
title Container diagram for Alexa Biblioteca Skill

System_Ext(alexa_platform, "Amazon Alexa Platform", "Voice Assistant Platform")
Container(ask, "Alexa Skills Kit", "Cloud Service", "Receives and processes voice commands")


Container_Boundary(lambda, "AWS Lambda Container") {
    Container(skill_app, "Biblioteca Skill Application", "AWS Lambda", "Skill logic executed on requests")
}

Container_Boundary(storage, "Storage Layer") {
    ContainerDb(s3db, "S3 Bucket", "S3", "Persistent Storage")
    Container(memcache, "Memory Cache", "In-memory Cache", "Temporary fast-access storage")

}

Rel(alexa_platform, ask, "Uses")
Rel(ask, skill_app, "Invokes on voice command intent")
Rel(skill_app, s3db, "Reads/Writes data")
Rel(skill_app, memcache, "Reads/Writes data")

```

#### Diagrama de Componentes (Level 3)

```mermaid
C4Component
    title Component diagram for Alexa Biblioteca Skill

    Container_Boundary(lambda_container, "AWS Lambda Container") {
        Component(lambda_handler, "Lambda Handler", "Python Module", "Entry point and request router")
        Component(intent_router, "Intent Router", "Dictionary", "Maps intents to handlers")

        Container_Boundary(handlers, "Intent Handlers Layer") {
            Component(agregar_handler, "Agregar Libro Handler", "Python Module", "Handles book creation")
            Component(listar_handler, "Listar Libros Handler", "Python Module", "Lists all books")
            Component(buscar_handler, "Buscar Libro Handler", "Python Module", "Searches books by title")
            Component(eliminar_handler, "Eliminar Libro Handler", "Python Module", "Deletes books")
            Component(prestar_handler, "Prestar Libro Handler", "Python Module", "Manages book loans")
            Component(devolver_handler, "Devolver Libro Handler", "Python Module", "Manages book returns")
            Component(consultar_p_handler, "Consultar Préstamos Handler", "Python Module", "Shows active loans")
            Component(consultar_d_handler, "Consultar Devueltos Handler", "Python Module", "Shows returned books")
            Component(decir_titulo_handler, "Decir Título Handler", "Python Module", "Contextual title handler")
            Component(limpiar_handler, "Limpiar Cache Handler", "Python Module", "Clears all data")
            Component(system_handlers, "System Handlers", "Python Modules", "Help, Stop, Fallback intents")
        }
    
        Container_Boundary(business, "Business Logic Layer") {
            Component(biblioteca_service, "Biblioteca Service", "Python Module", "Core business logic for library operations")
        }
    
        Container_Boundary(data_layer, "Data Access Layer") {
            Component(database_helper, "Database Helper", "Python Module", "State management")
            Component(session_state, "Session State Manager", "Python Object", "Manages libros, prestamos, devueltos")
        }
    
        Container_Boundary(utilities, "Utilities Layer") {
            Component(utils, "Utils", "Python Module", "Text normalization functions")
        }
    }

    Container_Boundary(storage, "Storage Layer") {
        ComponentDb(session_storage, "Session Attributes", "Alexa Session", "Temporary session storage")
    }

    System_Ext(alexa_service, "Alexa Service", "Amazon Alexa Platform")


  Rel(alexa_service, lambda_handler, "Sends IntentRequest", "HTTPS/JSON")
    Rel(lambda_handler, intent_router, "Uses")
    Rel(lambda_handler, database_helper, "Gets state")
  
    Rel(intent_router, agregar_handler, "Routes intent")
    Rel(intent_router, listar_handler, "Routes intent")
    Rel(intent_router, buscar_handler, "Routes intent")
    Rel(intent_router, eliminar_handler, "Routes intent")
    Rel(intent_router, prestar_handler, "Routes intent")
    Rel(intent_router, devolver_handler, "Routes intent")
    Rel(intent_router, consultar_p_handler, "Routes intent")
    Rel(intent_router, consultar_d_handler, "Routes intent")
    Rel(intent_router, decir_titulo_handler, "Routes intent")
    Rel(intent_router, limpiar_handler, "Routes intent")
    Rel(intent_router, system_handlers, "Routes intent")
  
    Rel(agregar_handler, biblioteca_service, "Calls add_book()")
    Rel(listar_handler, biblioteca_service, "Calls list_books()")
    Rel(buscar_handler, biblioteca_service, "Calls search_books()")
    Rel(eliminar_handler, biblioteca_service, "Calls delete_book()")
    Rel(prestar_handler, biblioteca_service, "Calls borrow_book()")
    Rel(devolver_handler, biblioteca_service, "Calls return_book()")
    Rel(decir_titulo_handler, biblioteca_service, "Calls add_book() / delete_book()")
  
    Rel(agregar_handler, session_state, "Modifies state")
    Rel(listar_handler, session_state, "Reads state")
    Rel(buscar_handler, session_state, "Reads state")
    Rel(eliminar_handler, session_state, "Modifies state")
    Rel(prestar_handler, session_state, "Modifies state")
    Rel(devolver_handler, session_state, "Modifies state")
    Rel(consultar_p_handler, session_state, "Reads state")
    Rel(consultar_d_handler, session_state, "Reads state")
    Rel(decir_titulo_handler, session_state, "Modifies state")
    Rel(limpiar_handler, session_state, "Clears state")
  
    Rel(biblioteca_service, utils, "Uses norm()")
    Rel(biblioteca_service, session_state, "Reads/Writes")
  
    Rel(database_helper, session_state, "Creates/Manages")
    Rel(session_state, session_storage, "Persists to", "Session Attributes")
  
    Rel(lambda_handler, alexa_service, "Returns response", "HTTPS/JSON")

 
```

**Enlaces a diagramas detallados:**

```plantuml
@startuml  
title C4 - Level 4 - Alexa Biblioteca Skill - Code Diagram

' ==================== ENUMS ====================
enum BookStatus {
    DISPONIBLE : "disponible"
    PRESTADO : "prestado"
}

' ==================== DOMAIN MODELS ====================
class Book {
    - id: str
    - titulo: str
    - autor: str
    - tipo: str
    - estado: BookStatus

    + to_dict() : dict
    + from_dict(data: dict) : Book
    + __str__() : str
}

class Prestamo {
    - libro_id: str
    - a: str

    + to_dict() : dict
    + from_dict(data: dict) : Prestamo
    + __str__() : str
}

' ==================== INTERFACES ====================
interface ISessionStorage {
  + get_state(event) : Dict[str, Any]
  + save_state(event, state: Dict[str, Any]) : None
}

interface IBookOperations {
  + add_book(state: Dict, titulo: str, autor: str, tipo: str) : Tuple[bool, Union[str, Book]]
  + list_books(state: Dict) : List[Book]
  + search_books(state: Dict, termino: str) : List[Book]
  + delete_book(state: Dict, titulo: str, libro_id: str) : Tuple[bool, Union[str, Book]]
}

interface ILoanOperations {
  + borrow_book(state: Dict, libro_or_title: str, persona: str) : Tuple[bool, str]
  + return_book(state: Dict, libro_or_title: str) : Tuple[bool, str]
}

' ==================== DATA LAYER ====================
class DatabaseHelper {
  + get_state(event) : Dict[str, Any]
  - _get_initial_state() : Dict[str, Any]
  - _validate_state(state: Dict) : Dict[str, Any]
}

class SessionState {
  + libros: List[Book]
  + prestamos: List[Prestamo]
  + devueltos: List[Prestamo]
  + __await__: Optional[str]
  
  + get_libros() : List[Book]
  + add_libro(libro: Book) : None
  + remove_libro(libro_id: str) : bool
  + clear() : None
}

' ==================== SERVICES ====================
class BibliotecaService {
  + add_book(state: Dict, titulo: str, autor: Optional[str], tipo: Optional[str]) : Tuple[bool, Union[str, Book]]
  + list_books(state: Dict) : List[Book]
  + search_books(state: Dict, termino: str) : List[Book]
  + delete_book(state: Dict, titulo: Optional[str], libro_id: Optional[str]) : Tuple[bool, Union[str, Book]]
  + borrow_book(state: Dict, libro_or_title: str, persona: Optional[str]) : Tuple[bool, str]
  + return_book(state: Dict, libro_or_title: str) : Tuple[bool, str]
  - _next_id(state: Dict) : str
  - _find_book(state: Dict, libro_id: str, titulo: str) : Optional[Book]
  - _is_book_loaned(state: Dict, libro_id: str) : bool
}

' ==================== UTILITIES ====================
class Utils {
  + norm(s: str) : str
}

' ==================== LAMBDA HANDLER ====================
class LambdaFunction {
  - _ROUTES: Dict[str, str]
  
  + lambda_handler(event, context) : Dict[str, Any]
  - _say(text: str, reprompt: str, end: bool, session: Dict) : Dict[str, Any]
  - _load_handler(intent_name: str) : Callable
  - _get_state(event: Dict) : Dict[str, Any]
}

' ==================== INTENT HANDLERS ====================
abstract class BaseHandler {
  # _slot(event: Dict, name: str) : Optional[str]
  + {abstract} handle(event: Dict, state: Dict) : Tuple[str, str]
}

class AgregarLibroHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
  - _validate_titulo(titulo: str) : bool
  - _request_titulo(state: Dict) : Tuple[str, str]
}

class ListarLibrosHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
  - _format_book_list(libros: List[Book], max_items: int) : str
}

class BuscarLibroHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
  - _format_search_results(resultados: List[Book]) : str
}

class EliminarLibroHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
  - _validate_deletion(state: Dict, libro_id: str) : bool
  - _request_titulo(state: Dict) : Tuple[str, str]
}

class PrestarLibroHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
  - _validate_loan(libro: Book) : bool
  - _request_libro(state: Dict) : Tuple[str, str]
}

class DevolverLibroHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
  - _validate_return(state: Dict, libro_id: str) : bool
  - _request_libro(state: Dict) : Tuple[str, str]
}

class ConsultarPrestamosHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
  - _format_prestamos(prestamos: List[Prestamo]) : str
}

class ConsultarDevueltosHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
  - _format_devueltos(devueltos: List[Prestamo]) : str
}

class DecirTituloHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
  - _handle_agregar_context(event: Dict, state: Dict, titulo: str) : Tuple[str, str]
  - _handle_eliminar_context(event: Dict, state: Dict, titulo: str) : Tuple[str, str]
  - _handle_no_context(titulo: str) : Tuple[str, str]
}

class LimpiarCacheHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
}

class HelpHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
}

class StopHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
}

class FallbackHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
}

class SiguientePaginaHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
}

class SalirListadoHandler {
  - _slot(event: Dict, name: str) : Optional[str]
  + handle(event: Dict, state: Dict) : Tuple[str, str]
}

' ==================== RELATIONSHIPS ====================

' Interface implementations
DatabaseHelper ..|> ISessionStorage
BibliotecaService ..|> IBookOperations
BibliotecaService ..|> ILoanOperations

' Lambda Function relationships
LambdaFunction --> DatabaseHelper : uses
LambdaFunction ..> AgregarLibroHandler : loads
LambdaFunction ..> ListarLibrosHandler : loads
LambdaFunction ..> BuscarLibroHandler : loads
LambdaFunction ..> EliminarLibroHandler : loads
LambdaFunction ..> PrestarLibroHandler : loads
LambdaFunction ..> DevolverLibroHandler : loads
LambdaFunction ..> ConsultarPrestamosHandler : loads
LambdaFunction ..> ConsultarDevueltosHandler : loads
LambdaFunction ..> DecirTituloHandler : loads
LambdaFunction ..> LimpiarCacheHandler : loads
LambdaFunction ..> HelpHandler : loads
LambdaFunction ..> StopHandler : loads
LambdaFunction ..> FallbackHandler : loads
LambdaFunction ..> SiguientePaginaHandler : loads
LambdaFunction ..> SalirListadoHandler : loads

' Handler inheritance
AgregarLibroHandler --|> BaseHandler
ListarLibrosHandler --|> BaseHandler
BuscarLibroHandler --|> BaseHandler
EliminarLibroHandler --|> BaseHandler
PrestarLibroHandler --|> BaseHandler
DevolverLibroHandler --|> BaseHandler
ConsultarPrestamosHandler --|> BaseHandler
ConsultarDevueltosHandler --|> BaseHandler
DecirTituloHandler --|> BaseHandler
LimpiarCacheHandler --|> BaseHandler
HelpHandler --|> BaseHandler
StopHandler --|> BaseHandler
FallbackHandler --|> BaseHandler
SiguientePaginaHandler --|> BaseHandler
SalirListadoHandler --|> BaseHandler

' Handler to Service dependencies
AgregarLibroHandler --> BibliotecaService : uses add_book()
ListarLibrosHandler --> BibliotecaService : uses list_books()
BuscarLibroHandler --> BibliotecaService : uses search_books()
EliminarLibroHandler --> BibliotecaService : uses delete_book()
PrestarLibroHandler --> BibliotecaService : uses borrow_book()
DevolverLibroHandler --> BibliotecaService : uses return_book()
DecirTituloHandler --> BibliotecaService : uses add_book(), delete_book()

' Handler to State dependencies
AgregarLibroHandler --> SessionState : modifies
ListarLibrosHandler --> SessionState : reads
BuscarLibroHandler --> SessionState : reads
EliminarLibroHandler --> SessionState : modifies
PrestarLibroHandler --> SessionState : modifies
DevolverLibroHandler --> SessionState : modifies
ConsultarPrestamosHandler --> SessionState : reads
ConsultarDevueltosHandler --> SessionState : reads
DecirTituloHandler --> SessionState : modifies
LimpiarCacheHandler --> SessionState : clears

' Service to Utils and State
BibliotecaService --> Utils : uses norm()
BibliotecaService --> SessionState : reads/writes

' DatabaseHelper to SessionState
DatabaseHelper --> SessionState : creates/manages

' Model relationships
SessionState *-- Book : contains
SessionState *-- Prestamo : contains
Book --> BookStatus : uses
Prestamo --> Book : references by libro_id

' Notes
note right of LambdaFunction
  Entry point for all Alexa requests.
  Routes intents to appropriate handlers
  using the _ROUTES dictionary.
end note

note right of BibliotecaService
  Core business logic layer.
  Handles all CRUD operations for books,
  loans, and returns. Uses Utils for
  text normalization.
end note

note right of SessionState
  In-memory state storage using
  Alexa sessionAttributes.
  Persists between intents within
  the same session.
end note

note right of DecirTituloHandler
  Context-aware handler that processes
  title input based on conversation state
  (__await__ flag in SessionState).
end note

@enduml
```

---

## 6. Diseño VUI / Diagramas de flujo de voz

### Objetivo del diseño VUI

Crear una experiencia de voz natural e intuitiva que simule una conversación con un bibliotecario personal, minimizando la fricción y maximizando la comprensión.

### Estilo, tono y lenguaje de voz

* **Tono:** Amigable, servicial y profesional
* **Personalidad:** Bibliotecario experto pero accesible
* **Lenguaje:** Español mexicano, formal pero cercano
* **Respuestas:** Variadas para evitar repetición, confirmaciones claras

### Escenarios de uso por voz

* **Cuándo:** En casa, durante organización de libros, antes/después de préstamos
* **Dónde:** Biblioteca personal, estudio, sala de estar
* **Dispositivos:** Echo Dot, Echo Show, dispositivos móviles con Alexa
* **Entorno:** Silencioso a moderadamente ruidoso

### Diagramas de flujo de conversación DIAGRAMA

```plantuml
@startuml Master
    ' Master – Navegación principal de intents (es-MX)
    skinparam shadowing false
    skinparam state {
    BackgroundColor #f8f8f8
    BorderColor #888
    RoundCorner 12
    }

    [*] --> Launch
    state Launch {
    [*] --> Bienvenida
    Bienvenida : Saludo + estado + opciones + pregunta
    Bienvenida --> Menu : usuario responde
    }

    state Menu {
    [*] --> EsperaComando
    EsperaComando --> AgregarLibro : AgregarLibroIntent
    EsperaComando --> Listar : ListarLibrosIntent
    EsperaComando --> Buscar : BuscarLibroIntent
    EsperaComando --> Prestar : PrestarLibroIntent
    EsperaComando --> Devolver : DevolverLibroIntent
    EsperaComando --> VerPrestamos : ConsultarPrestamosIntent
    EsperaComando --> VerDevueltos : ConsultarDevueltosIntent
    EsperaComando --> LimpiarCache : LimpiarCacheIntent
    EsperaComando --> MostrarOpciones : MostrarOpcionesIntent
    EsperaComando --> [*] : AMAZON.StopIntent / AMAZON.CancelIntent
    EsperaComando --> Ayuda : AMAZON.HelpIntent
    EsperaComando --> Fallback : AMAZON.FallbackIntent
    }

    state AgregarLibro {
    [*] --> PasoTitulo
    PasoTitulo : Elicit título (si falta)
    PasoTitulo --> PasoAutor : titulo capturado
    PasoAutor : Elicit autor (permite "no sé" → Desconocido)
    PasoAutor --> PasoTipo : autor capturado o Desconocido
    PasoTipo : Elicit tipo (permite "no sé" → Sin categoría)
    PasoTipo --> ConfirmAlta : título+autor+tipo
    ConfirmAlta : Guarda libro + stats + limpia sesión
    ConfirmAlta --> Menu : cierre + "¿algo más?"
    }

    state Listar {
    [*] --> Preparar
    Preparar : Sincroniza estados → aplica filtros (filtro_tipo|autor)
    Preparar --> Paginando
    state Paginando {
        [*] --> PaginaN
        PaginaN : Lee pagina_libros y responde (10 ítems)
        PaginaN --> PaginaN : SiguientePaginaIntent / avanza índice
        PaginaN --> Menu : SalirListadoIntent o fin de lista
        PaginaN --> FallbackListando : AMAZON.FallbackIntent (contexto paginado)
    }
    }

    state Buscar {
    [*] --> ElicitTitulo
    ElicitTitulo : Si falta titulo → pedir
    ElicitTitulo --> MostrarResultado : 1 resultado → ficha
    ElicitTitulo --> MostrarCoincidencias : n>1 → top 3
    ElicitTitulo --> SinResultados : n=0 → sugerencias
    MostrarResultado --> Menu
    MostrarCoincidencias --> Menu
    SinResultados --> Menu
    }

    state Prestar {
    [*] --> ElicitTitulo
    ElicitTitulo : Si falta titulo → pedir
    ElicitTitulo --> ValidarLibro
    ValidarLibro : Buscar exacto en biblioteca
    ValidarLibro --> NoEncontrado : si no existe (sugerir disponibles)
    ValidarLibro --> YaPrestado : si libro_id en préstamos
    ValidarLibro --> RegistrarPrestamo : si disponible
    RegistrarPrestamo : Crea préstamo + fecha_limite + stats
    RegistrarPrestamo --> Menu
    YaPrestado --> Menu
    NoEncontrado --> Menu
    }

    state Devolver {
    [*] --> ElicitDato
    ElicitDato : Pide título o id_prestamo
    ElicitDato --> EncontrarPrestamo
    EncontrarPrestamo : Match por id o por título (contains)
    EncontrarPrestamo --> NoMatch : si no encuentra (muestra sugerencias)
    EncontrarPrestamo --> ProcesarDevolucion : si encuentra
    ProcesarDevolucion : Mueve a historial, marca disponible, +stats, msg tiempo
    ProcesarDevolucion --> Menu
    NoMatch --> Menu
    }

    state VerPrestamos {
    [*] --> Reporte
    Reporte : Lista activos (máx 5), marca vencidos/por vencer
    Reporte --> Menu
    }

    state VerDevueltos {
    [*] --> Reporte
    Reporte : Lista todos (≤10) o 5 recientes
    Reporte --> Menu
    }

    state LimpiarCache {
    [*] --> Ejecutar
    Ejecutar : Limpia _CACHE → get_user_data → sincroniza → guarda
    Ejecutar --> Menu
    }

    state MostrarOpciones {
    [*] --> DecirMenu
    DecirMenu : Copys de opciones + contexto + pregunta
    DecirMenu --> Menu
    }

    state Ayuda {
    [*] --> DecirAyuda
    DecirAyuda : Guía de comandos
    DecirAyuda --> Menu
    }

    state Fallback {
    [*] --> Manejar
    Manejar : Mensaje genérico + recordatorio de capacidades
    Manejar --> Menu
    }

    Launch --> Menu
@enduml

```

#### Flujo Principal - Agregar Libro DIAGRAMA

```plantuml
@startuml AgregarLibro
    ' AgregarLibro – Captura progresiva (titulo→autor→tipo)
    skinparam shadowing false

    [*] --> Inicio
    Inicio --> ElicitTitulo : AgregarLibroIntent sin titulo
    Inicio --> ElicitAutor : con titulo, sin autor
    Inicio --> ElicitTipo : con titulo+autor, sin tipo
    Inicio --> ConfirmAlta : con todos

    ElicitTitulo : "¿Cuál es el título?"
    ElicitTitulo --> ElicitAutor : usuario dice titulo (ContinuarAgregar captura slots)
    ElicitTitulo --> ElicitTitulo : Fallback/no entendido → tips "el título es ..."

    ElicitAutor : "¿Quién es el autor? (di: no sé)"
    ElicitAutor --> ElicitTipo : autor
    ElicitAutor --> ElicitTipo : "no sé" → autor=Desconocido
    ElicitAutor --> ElicitAutor : Fallback → tips "el autor es ..."

    ElicitTipo : "¿De qué tipo/género es? (di: no sé)"
    ElicitTipo --> ConfirmAlta : tipo
    ElicitTipo --> ConfirmAlta : "no sé" → tipo=Sin categoría
    ElicitTipo --> ElicitTipo : Fallback → tips "el tipo es ..."

    ConfirmAlta : Crea libro {id, titulo, autor, tipo, fecha, estado=disponible}
    ConfirmAlta : ++estadisticas.total_libros; limpia sesión
    ConfirmAlta --> Exito

    Exito : "Agregado '{titulo}'. Ahora tienes N libros. ¿Algo más?"
    Exito --> [*]
@enduml

```

#### Flujo - Eliminar Libro (Nuevo) DIAGRAMA

```mermaid
graph TD
    A["Usuario: Elimina un libro"] --> B["Sistema: ¿Qué libro quieres eliminar?"]
    B --> C["Usuario: Dice título"]
    C --> D{"¿Libro encontrado?"}
    D -->|Sí| E["Sistema: ¿Estás seguro de eliminar X?"]
    D -->|No| F["Sistema: No encontré ese libro"]
    F --> G["Sistema: Sugiere libros disponibles"]
    G --> C
    E --> H["Usuario: Sí o No"]
    H -->|Sí| I{"¿Libro prestado?"}
    H -->|No| J["Sistema: Ok, no lo elimino"]
    I -->|No| K["Sistema: Elimina y confirma"]
    I -->|Sí| L["Sistema: Está prestado, ¿eliminar igual?"]
    L --> M["Usuario: Confirma"]
    M -->|Sí| N["Sistema: Elimina y cancela préstamo"]
    M -->|No| J

```

#### Flujo - Manejo de Errores DIAGRAMA

```mermaid
graph TD
    A[Error/Excepción] --> B{¿Tipo de error?}
    B -->|Timeout| C["Sistema: 'Tardaste mucho, empecemos de nuevo'"]
    B -->|No entendido| D["Sistema: 'No entendí, ¿puedes repetir?'"]
    B -->|Fallo técnico| E["Sistema: 'Hubo un problema técnico'"]
    B -->|Cancelación| F["Sistema: 'Ok, cancelado'"]
  
    C --> G[Regresar al menú principal]
    D --> H[Repetir última pregunta]
    E --> G
    F --> G
```

### Consideraciones especiales

* **Latencia:** Respuestas en < 2 segundos para mantener fluidez
* **Reconocimiento:** Manejo de variaciones en pronunciación de títulos
* **Fallbacks:** Múltiples niveles de clarificación antes de cancelar
* **Context:** Mantener contexto durante diálogos multi-turno
* **Confirmaciones:** Siempre confirmar acciones destructivas

Ver mas diagrmas en ./VUI_diagrams

---

## 7. Secciones adicionales

##Modelo de datos

##Libro
```markdown
{
"id": str, # se genera automáticamente
"titulo": str, # normalizado para evitar duplicados
"autor": str, # "Desconocido" si no se brinda
"tipo": str, # género o categoría del libro
"estado": str # "disponible" o "prestado"
}
```
##Loan
```markdown
# Prestamos activos
{"libro_id": str, "persona": str}

# Devueltos
{"libro_id": str, "persona": str}
```

## 8. Apéndices

### Decisiones de diseño importantes

1. **Patrón Repository:** Abstrae el acceso a datos permitiendo cambiar de S3 a otra base de datos
2. **Service Layer:** Centraliza lógica de negocio evitando duplicación
3. **Factory Pattern:** Para crear diferentes tipos de adapters (S3, Fake, DynamoDB)

---

## 9. Revisión y mantenimiento del documento

### Proceso de refactorización aplicado

#### Análisis del monolito original

El archivo `lambda_function.py` original presentaba los siguientes problemas estructurales:

1. **Violación del Single Responsibility Principle:** Los handlers manejaban lógica de negocio, validación y persistencia
2. **Alto acoplamiento:** Cambios en persistencia requerían modificar múltiples handlers
3. **Código duplicado:** Lógica de validación y respuestas repetida
4. **Difícil testing:** Imposible probar componentes por separado

### Estrategia de desacoplamiento

#### Paso 1: Identificación de responsabilidades

```markdown
Monolito original → Responsabilidades identificadas:
- Manejo de requests/responses Alexa → Handlers (Presentation)
- Lógica de negocio → Services (Business)
- Acceso a datos → Repositories (Data)
- Modelos de datos → Models (Domain)
- Utilidades → Utils (Infrastructure)
```

#### Paso 2: Aplicación de principios SOLID

1. **Single Responsibility Principle:**
   * Cada handler maneja solo un intent específico
   * Services contienen solo lógica de un dominio
   * Repositories solo acceso a datos
2. **Open/Closed Principle:**
   * Interfaces para adapters permiten extensión sin modificación
   * Nuevos tipos de libros se agregan sin cambiar código existente
3. **Liskov Substitution Principle:**
   * S3Adapter y FakeS3Adapter son intercambiables
   * Diferentes estrategias de cache implementan misma interfaz
4. **Interface Segregation Principle:**
   * Interfaces específicas para cada tipo de operación
   * No dependencias en métodos no utilizados
5. **Dependency Inversion Principle:**
   * Services dependen de abstracciones, no implementaciones
   * Inyección de dependencias en constructores

#### Paso 3: Reestructuración de archivos

```markdown
Estructura final:
lambda_function.py
├── handlers/
│ ├── agregar.py
│ ├── listar.py
│ ├── eliminar.py
│ ├── prestar.py
│ ├── devolver.py
│ └── otros handlers
├── services/
│ └── biblioteca_service.py
├── helpers/
│ └── database.py
├── shared/
│ └── utils.py
└── utils.py
```

**Decisiones clave tomadas:**

1. **Separación de Book y Loan Services:** Aunque están relacionados, tienen ciclos de vida diferentes y responsabilidades distintas
2. **Repository por entidad:** Permite optimizaciones específicas para cada tipo de datos
3. **Adapter pattern para persistencia:** Facilita testing con FakeS3Adapter y futuras migraciones
4. **Central response builder:** Evita duplicación de lógica de construcción de respuestas Alexa

### Historial de Revisión / Mantenimiento


| Versión | Fecha    | Autor(es)               | Cambios Realizados                                      | Aprobado por           | Comentarios adicionales               |
| -------- | -------- | ----------------------- | ------------------------------------------------------- | ---------------------- | ------------------------------------- |
| 0.1      | 22-09-25 | Equipo completo         | Creación inicial del documento; análisis del monolito | Líder del equipo      | Primer borrador con casos de uso      |
| 0.5      | 27-09-25 | Desarrollador principal | Incorporación de diagramas C4 y arquitectura           | Arquitecto de software | Revisión de patrones aplicados       |
| 0.8      | 27-09-25 | UX Designer             | Adición de flujos VUI y diagramas de voz               | Product Owner          | Validación de experiencia de usuario |
| 1.0      | xxxxxxxx | Equipo completo         | Documento aprobado con apéndice de refactorización    | Líder del equipo      | Versión final para implementación   |
