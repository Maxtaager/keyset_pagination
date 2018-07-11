from keyset_pagination.models import KeySetModel
from keyset_pagination.mixins import KeysetPaginationMixin


class Index(KeysetPaginationMixin):
    template_name = 'keyset_pagination/index.html'
    paginate_by = 5
    reverse = False
    model = KeySetModel