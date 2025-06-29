from contrib.module_manager import AppModule

from .application import controllers, interactors
from .application.boundaries import repositories as repositories_interfaces
from .infrastructure import repositories


class CatalogModule(AppModule):
    imports = []
    dependencies = []
    exports = [
        # Контроллеры
        controllers.CategoryController,
        controllers.ProductController,
        # Интеракторы
        interactors.ProductInteractor,
        interactors.CategoryInteractor,
        # Репозитории
        repositories.ProductRepository,
        repositories.CategoryRepository,
    ]
    providers = [
        # Контроллеры
        controllers.CategoryController,
        controllers.ProductController,
        # Интеракторы
        interactors.ProductInteractor,
        interactors.CategoryInteractor,
        # Репозитории
        repositories.ProductRepository,
        repositories.CategoryRepository,
    ]
    mapping = {
        # Репозитории
        repositories_interfaces.IProductRepository: repositories.ProductRepository,
        repositories_interfaces.ICategoryRepository: repositories.CategoryRepository,
    }
