from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(Path(__file__).resolve().parent / ".env"),
            str(Path(__file__).resolve().parent.parent / ".env"),
        ),
        extra="ignore",
    )

    session_secret: str = Field(..., env="SESSION_SECRET")
    session_https_only: bool = Field(True, env="SESSION_HTTPS_ONLY")
    session_max_age_seconds: int = Field(3600, env="SESSION_MAX_AGE_SECONDS")
    session_same_site: str = Field("lax", env="SESSION_SAMESITE")
    session_cookie_name: str = Field("pm_session", env="SESSION_COOKIE_NAME")

    frontend_origins: str = Field("http://localhost:5173", env="FRONTEND_ORIGINS")

    aws_region: str = Field(..., env="AWS_REGION")
    s3_bucket: str = Field(..., env="S3_BUCKET")
    kms_key_arn: str = Field(..., env="KMS_KEY_ARN")
    vault_prefix: str = Field("vaults", env="VAULT_PREFIX")

    cognito_user_pool_id: str = Field(..., env="COGNITO_USER_POOL_ID")
    cognito_client_id: str = Field(..., env="COGNITO_CLIENT_ID")
    cognito_client_secret: str = Field(
        ...,
        validation_alias=AliasChoices("COGNITO_CLIENT_SECRET", "AUTH_CLIENT_SECRET"),
    )
    cognito_domain: str = Field(..., env="COGNITO_DOMAIN")
    cognito_redirect_uri: str = Field(..., env="COGNITO_REDIRECT_URI")
    cognito_region: Optional[str] = Field(None, env="COGNITO_REGION")
    cognito_scopes: str = Field("openid email", env="COGNITO_SCOPES")

    @property
    def effective_cognito_region(self) -> str:
        return self.cognito_region or self.aws_region

    @property
    def cognito_metadata_url(self) -> str:
        return (
            f"https://cognito-idp.{self.effective_cognito_region}.amazonaws.com/"
            f"{self.cognito_user_pool_id}/.well-known/openid-configuration"
        )

    @property
    def frontend_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        ]

    @property
    def frontend_app_origin(self) -> str:
        origins = self.frontend_origin_list
        if origins:
            return origins[0]
        return "http://localhost:5173"

    @property
    def frontend_app_url(self) -> str:
        return f"{self.frontend_app_origin.rstrip('/')}/"

    @property
    def frontend_login_url(self) -> str:
        return f"{self.frontend_app_origin.rstrip('/')}/login"

    @property
    def cognito_domain_host(self) -> str:
        raw = self.cognito_domain.strip()
        parsed = urlparse(raw)
        if parsed.netloc:
            return parsed.netloc
        if parsed.path:
            return parsed.path.strip("/")
        return raw.rstrip("/")


settings = Settings()
