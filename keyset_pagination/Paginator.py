import collections

import six
from django.core.paginator import Page, InvalidPage
from django.utils.translation import ugettext_lazy as _


class PageParamInvalid(InvalidPage):
    pass


class KeysetPage(collections.Sequence):
    def __init__(self, object_list, paginator, backwards_scrolling=False):
        self.paginator = paginator
        self._has_next = False
        self._has_previous = False
        self.first_id = None
        self.last_id = None
        self.backwards_scrolling = backwards_scrolling
        self.object_list = []
        if object_list:
            self._set_first_and_last_id(object_list, backwards_scrolling)
            self.object_list = object_list[:self.paginator.per_page]
            if backwards_scrolling:
                # when we are scrolling backwards we need to reverse the result list
                self.object_list.reverse()

    def _set_first_and_last_id(self, object_list, backwards_scrolling):
        if len(object_list) == self.paginator.per_page+1:
            # we have one extra element so we have more pages
            if backwards_scrolling:
                self.last_id = object_list[0].id
                self.first_id = object_list[-2].id
            else:
                self.last_id = object_list[-2].id
                self.first_id = object_list[0].id
        else:
            # anything less than self.paginator.per_page+1 means last page
            if self.backwards_scrolling:
                self.last_id = object_list[0].id
                self.first_id = None
            else:
                self.last_id = None
                self.first_id = object_list[0].id

    def __repr__(self):
        if len(self.object_list) == 0:
            return '<no items found>'
        s = ''
        if self.has_previous():
            s = '<previous> '
        if self.has_next():
            s = s+'<next>'
        return s

    def __getitem__(self, index):
        if not isinstance(index, (slice,) + six.integer_types):
            raise TypeError
        return self.object_list[index]

    def __len__(self):
        return len(self.object_list)

    def has_other_pages(self):
        return self.has_next() or self.has_previous()

    def has_previous(self):
        if self.paginator.first_page:
            return False

        if self.paginator.reverse and self.first_id:
            return self.first_id - self.paginator.per_page >= 0
        else:
            return self.first_id is not None

    def has_next(self):
        return self.last_id is not None


class KeysetPaginator(object):
    """
     assumptions:
     1: olny works with postgresql
     2: ids start with 1
     3: we do not reuse ids after an row is deleted (postgresql dosent do this)
    """
    name = 'keyset'

    def __init__(self, query_set, per_page, reverse=False):
        self.query_set = query_set
        self.per_page = per_page
        self.reverse = reverse
        self.backwards_scrolling = False
        self._page = None
        self.first_page = False

    def page(self, first_id, last_id):
        if first_id is not None:
            first_id = self.validate_pagination_params(first_id)
        if last_id is not None:
            last_id = self.validate_pagination_params(last_id)
        if last_id is None and first_id is None:
            self.first_page = True
        else:
            self.first_page = False
        objects = self.get_page_items(first_id, last_id)
        return KeysetPage(objects, self, self.backwards_scrolling)

    def get_page_items(self, first_id, last_id):
        if first_id is None and last_id is None:
            # first page
            qs = self.query_set
            if self.reverse is False:
                qs = qs.order_by('id')
            else:
                qs = qs.order_by('-id')
            return list(qs[:self.per_page + 1])

        elif last_id and first_id is None:
            # forward scrolling
            if self.reverse is False:
                return list(self.query_set.filter(id__gt=last_id).order_by('id')[:self.per_page + 1])
            else:
                return list(self.query_set.filter(id__lt=last_id).order_by('-id')[:self.per_page + 1])

        elif first_id and last_id is None:
            # backwards scrolling
            self.backwards_scrolling = True
            if self.reverse is False:
                return list(self.query_set.filter(id__lt=first_id).order_by('-id')[:self.per_page + 1])
            else:
                return list(self.query_set.filter(id__gt=first_id).order_by('id')[:self.per_page + 1])

    def validate_pagination_params(self,  param):
        try:
            param = int(param)
        except ValueError:
            raise PageParamInvalid(_('page param needs to be integer? but was not'))
        if param == 0: # we allow 0 to be passed but lets just set it to None to keep complexity down in the later code.
            param = None
        return param