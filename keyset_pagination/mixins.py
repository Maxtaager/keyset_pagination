from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import InvalidPage
from django.db.models import QuerySet
from django.http import Http404
from django.utils.encoding import force_text
from django.views.generic import ListView
from keyset_pagination.Paginator import KeysetPaginator


class KeysetPaginationMixin(ListView):
    first_id_kwarg = 'first_id'
    last_id_kwarg = 'last_id'
    reverse = False

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
                #TODO check if it was ordered and if so raise an error
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        return queryset

    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        queryset = self.get_queryset()
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        if page_size:
            paginator, page, object_list, is_paginated = self.paginate_queryset(queryset, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': object_list,
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset,
            }
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        if 'view' not in kwargs:
            context.update({'view': self})
        return context

    def paginate_queryset(self, queryset, page_size):
        first_id_kwarg = self.first_id_kwarg
        first_id = self.request.GET.get(first_id_kwarg)

        last_id_kwarg = self.last_id_kwarg
        last_id = self.request.GET.get(last_id_kwarg)
        if first_id and last_id:
            # you cant provide last_id and first_id then we dont know which one to use...
            raise Http404(_('Invalid page (%(page_size)s): %(message)s') % {
                'page_size': page_size,
                'message': '',
            })

        paginator = KeysetPaginator(queryset, page_size, reverse=self.reverse)

        try:
            page = paginator.page(first_id, last_id)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            #TODO: write some proper text
            raise Http404(_('Invalid page (%(page_size)s): %(message)s') % {
                'page_size': page_size,
                'message': force_text(e),
            })