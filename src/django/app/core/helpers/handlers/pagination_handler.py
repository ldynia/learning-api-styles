from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageNumberPaginationHATEOAS(PageNumberPagination):

    def get_paginated_response(self, data, status_code: int = 200):
        return Response({
            "_links": {
                "self": {
                    "href": self.request.build_absolute_uri(),
                    "method": "GET",
                    "rel": "self",
                    "type": "application/json"
                },
                "next": {
                    "href": self.get_next_link(),
                    "method": "GET" if self.page.has_next() else None,
                    "rel": "self" if self.page.has_next() else None,
                    "type": "application/json" if self.page.has_next() else None
                },
                "previous": {
                    "href": self.get_previous_link(),
                    "method": "GET" if self.page.has_previous() else None,
                    "rel": "self" if self.page.has_previous() else None,
                    "type": "application/json" if self.page.has_previous() else None
                }
            },
            "pagination": {
                "has_next_page": self.page.has_next(),
                "has_previous_page": self.page.has_previous(),
                "current_page_index": self.page.number,
                "next_page_index": self.page.next_page_number() if self.page.has_next() else None,
                "previous_page_index": self.page.previous_page_number() if self.page.has_previous() else None,
                "items_per_page": self.page.paginator.per_page,
                "total_page_count": self.page.paginator.num_pages,
                "total_item_count": self.page.paginator.count
            },
            "data": data
        }, status_code)
