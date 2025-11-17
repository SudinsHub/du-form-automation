from abc import ABC
from sqlalchemy.orm import Session

class BaseService(ABC):
    """Base service class with common functionality"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _validate_entity_exists(self, entity, entity_name: str, entity_id: any):
        """Common validation method"""
        if not entity:
            raise ValueError(f"{entity_name} with id {entity_id} not found")
        return entity