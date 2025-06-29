from __future__ import annotations

import abc

from django.http import Http404
from django.views.generic import View


class CheckPageAvailableMixin(View):
    """Миксин проверки доступности страницы"""

    __metaclass__ = abc.ABCMeta

    def dispatch(self, request, *args, **kwargs):
        if not self.check_page_available(request.user, *args, **kwargs):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    @abc.abstractmethod
    def check_page_available(self, user, *args, **kwargs):
        """Логика проверки доступности страница"""
