from contrib.module_manager import AppModule

from .application import controllers, interactors
from .application.boundaries import repositories as repositories_interfaces
from .infrastructure import repositories


class OrderModule(AppModule):
    imports = ["catalog"]
    dependencies = ["catalog"]
    exports = [
        # Контроллеры
        controllers.OrderController,
        # Интеракторы
        interactors.OrderInteractor,
        # Репозитории
        repositories.OrderStatusRepository,
        repositories.OrderItemRepository,
        repositories.OrderRepository,
    ]
    providers = [
        # Контроллеры
        controllers.OrderController,
        # Интеракторы
        interactors.OrderInteractor,
        # Репозитории
        repositories.OrderStatusRepository,
        repositories.OrderItemRepository,
        repositories.OrderRepository,
    ]
    mapping = {
        # Репозитории
        repositories_interfaces.IOrderStatusRepository: repositories.OrderStatusRepository,
        repositories_interfaces.IOrderItemRepository: repositories.OrderItemRepository,
        repositories_interfaces.IOrderRepository: repositories.OrderRepository,
    }
