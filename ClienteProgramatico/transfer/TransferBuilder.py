from typing import List
import uuid
from transfer.Transfer import Transfer
from transfer.DataDestinationBuilder import DataDestinationBuilder


class TransferBuilder:
    """Construtor principal para o Transfer completo."""
    
    def __init__(self):
        self._trasfer = Transfer()
    
    def with_asset_id(self, asset_id: str) -> 'TransferBuilder':
        """Define o ID do asset."""
        self._trasfer.asset_id = asset_id
        return self
    
    def with_contract_id(self, contract_id) -> 'TransferBuilder':
        """Define o id do contrato."""
        self._trasfer.contract_id = contract_id
        return self
    
    def with_data_destination(self, data_destination_builder: DataDestinationBuilder) -> 'TransferBuilder':
        """Define o DataAddress usando um construtor específico."""
        self._trasfer.data_destination = data_destination_builder.build()
        return self
    
    def with_transfer_type(self,transfer_type) -> 'TransferBuilder':
        """Define o transfer type"""
        self._trasfer.transfer_type = transfer_type
        return self

    def build(self) -> Transfer:
        """Constrói e retorna o Transfer configurado."""
        return self._trasfer