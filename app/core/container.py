from dependency_injector import containers, providers

from app import repositories, services
from app.core.config import configs
from app.core.database import Database


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            # "app.api.v1.endpoints.admin",
            "app.api.v1.endpoints.auth",
            "app.api.v1.endpoints.user",
        ]
    )
    db = providers.Singleton(Database, db_url=configs.DB_URL, sync_db_url=configs.SYNC_DB_URL)

    # Base repositories
    user_repository = providers.Factory(repositories.UserRepository, session_factory=db.provided.session_factory)

    # Base services
    auth_service = providers.Factory(services.AuthService, user_repository=user_repository)
    user_service = providers.Factory(services.UserService, user_repository=user_repository)

    # # Integrated services
    # cms_integrated_service = providers.Factory(
    #     services.CmsIntegratedService,
    #     user_service=user_service,
    # )