from app.services.credentials import CredentialService
from app.services.schema_retriever import SchemaRetriever


def test_credentials_round_trip() -> None:
    service = CredentialService("test-secret")
    assert service.decrypt(service.encrypt("password")) == "password"


def test_connection_response_model_has_no_password_field() -> None:
    from app.schemas.databases import DatabaseConnectionResponse
    assert "password" not in DatabaseConnectionResponse.model_fields
    assert "encrypted_password" not in DatabaseConnectionResponse.model_fields
