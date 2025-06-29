from __future__ import annotations

from rest_framework.renderers import BaseRenderer


class XLSRenderer(BaseRenderer):
    media_type = "application/xls"
    format = "xls"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data
