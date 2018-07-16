from sample.models import KeySetModel
from keyset_pagination.mixins import KeysetPaginationMixin


class Index(KeysetPaginationMixin):
    template_name = 'sample/index.html'
    paginate_by = 5
    reverse = False
    model = KeySetModel