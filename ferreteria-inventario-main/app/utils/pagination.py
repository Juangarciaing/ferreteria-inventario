"""
Sistema de Paginación para APIs
Maneja grandes volúmenes de datos dividiéndolos en páginas
"""
from typing import List, Dict, Any, TypeVar, Generic
from math import ceil

T = TypeVar('T')

class PaginatedResponse(Generic[T]):
    """
    Clase para respuestas paginadas
    Incluye datos, metadata de paginación y navegación
    """
    
    def __init__(
        self,
        items: List[T],
        page: int,
        per_page: int,
        total_items: int
    ):
        """
        Args:
            items: Lista de items de la página actual
            page: Número de página actual (1-indexed)
            per_page: Cantidad de items por página
            total_items: Total de items en la base de datos
        """
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total_items = total_items
        self.total_pages = ceil(total_items / per_page) if per_page > 0 else 0
        self.has_prev = page > 1
        self.has_next = page < self.total_pages
        self.prev_page = page - 1 if self.has_prev else None
        self.next_page = page + 1 if self.has_next else None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la respuesta paginada a diccionario para JSON
        
        Returns:
            {
                "items": [...],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total_items": 150,
                    "total_pages": 8,
                    "has_prev": false,
                    "has_next": true,
                    "prev_page": null,
                    "next_page": 2
                }
            }
        """
        return {
            "items": self.items,
            "pagination": {
                "page": self.page,
                "per_page": self.per_page,
                "total_items": self.total_items,
                "total_pages": self.total_pages,
                "has_prev": self.has_prev,
                "has_next": self.has_next,
                "prev_page": self.prev_page,
                "next_page": self.next_page
            }
        }


def paginate_query(query, page: int = 1, per_page: int = 20, max_per_page: int = 100):
    """
    Pagina una query de SQLAlchemy
    
    Args:
        query: Query de SQLAlchemy
        page: Número de página (default: 1)
        per_page: Items por página (default: 20)
        max_per_page: Máximo permitido por página (default: 100)
    
    Returns:
        PaginatedResponse con los resultados
    
    Example:
        query = Producto.query.filter_by(categoria_id=1)
        result = paginate_query(query, page=2, per_page=10)
        return jsonify(result.to_dict())
    """
    # Validar y limitar parámetros
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    
    # Obtener total de items (antes de paginar)
    total_items = query.count()
    
    # Aplicar paginación a la query
    # offset = (page - 1) * per_page
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    
    return PaginatedResponse(
        items=items,
        page=page,
        per_page=per_page,
        total_items=total_items
    )


def paginate_list(items_list: List[T], page: int = 1, per_page: int = 20) -> PaginatedResponse[T]:
    """
    Pagina una lista de Python (ya cargada en memoria)
    Útil cuando ya tienes los datos filtrados
    
    Args:
        items_list: Lista de items a paginar
        page: Número de página
        per_page: Items por página
    
    Returns:
        PaginatedResponse con los items de la página
    
    Example:
        productos = [p1, p2, p3, ...]  # 100 productos
        result = paginate_list(productos, page=1, per_page=10)
        # Retorna los primeros 10
    """
    page = max(1, page)
    per_page = max(1, per_page)
    total_items = len(items_list)
    
    # Calcular índices de slice
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Obtener items de la página
    page_items = items_list[start_idx:end_idx]
    
    return PaginatedResponse(
        items=page_items,
        page=page,
        per_page=per_page,
        total_items=total_items
    )


def get_pagination_params(request) -> tuple:
    """
    Extrae parámetros de paginación de un Flask request
    
    Args:
        request: Flask request object
    
    Returns:
        (page, per_page) como tupla de enteros
    
    Query params esperados:
        - page: número de página (default: 1)
        - per_page: items por página (default: 20, max: 100)
    
    Example:
        GET /api/productos?page=2&per_page=10
        page, per_page = get_pagination_params(request)
        # page=2, per_page=10
    """
    try:
        page = int(request.args.get('page', 1))
    except (ValueError, TypeError):
        page = 1
    
    try:
        per_page = int(request.args.get('per_page', 20))
    except (ValueError, TypeError):
        per_page = 20
    
    # Limitar valores
    page = max(1, page)
    per_page = max(1, min(per_page, 100))  # Máximo 100 por página
    
    return page, per_page
