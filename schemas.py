from pydantic import BaseModel
from typing import List

class VariableSuggestion(BaseModel):
    nombre: str
    tipo_sugerido: str

class ConfirmVariablesResponse(BaseModel):
    variables: List[VariableSuggestion]
