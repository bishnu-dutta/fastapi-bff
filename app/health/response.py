from pydantic import BaseModel, ConfigDict, Field


class PingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ping: str = Field(
        default="pong",
        description="Echo response confirming service is alive",
    )


class HealthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str = Field(
        default="healthy",
        description="Overall application health status ('healthy', 'degraded', or 'unhealthy')",
    )
    app: str = Field(
        description="Application name",
    )
    version: str = Field(
        description="Application version",
    )
    directus: str = Field(
        default="connected",
        description="Directus upstream status ('connected' or 'unavailable')",
    )
    keycloak: str = Field(
        default="connected",
        description="Keycloak upstream status ('connected' or 'unavailable')",
    )