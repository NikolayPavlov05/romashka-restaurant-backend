from __future__ import annotations

from contrib.clean_architecture.utils.query_dict import FindFilter
from contrib.clean_architecture.utils.query_dict import parse_query_dict
from contrib.clean_architecture.utils.query_dict import Wrappers
from django.db.models import F
from django.db.models import Q


class TestQueryDictUtil:
    def test_positive(self):
        """Тестируем функцию"""
        filters = {
            "field1__gte": 1,
            "~field2": 2,
            "condition__and": {
                "condition__or": {"field3__lte": 3, "field4": 4, "~field5": 5},
                "~field6__gte": 6,
            },
            "~condition__and": {
                "~condition__or": {"field7__lte": 7, "field8": 8, "~field9": 9},
                "~field10__gte": 10,
            },
            "field10_f": FindFilter("test"),
            "~field11_f": FindFilter("test"),
        }
        query: Q = (
            Q(Q(field1__gte=1))
            & Q(~Q(field2=2))
            & Q(Q(Q(Q(field3__lte=3)) | Q(Q(field4=4)) | Q(~Q(field5=5))) & ~Q(field6__gte=6))
            & ~Q(~Q(Q(Q(field7__lte=7)) | Q(Q(field8=8)) | ~Q(field9=9)) & ~Q(field10__gte=10))
            & Q(Q(field10_f=F("test")))
            & ~Q(field11_f=F("test"))
        )

        result = parse_query_dict("", filters, wrappers=Wrappers(condition=Q, find=F))

        assert result is not None
        assert result == query

        # TODO: На фейк
