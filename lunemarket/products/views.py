from django.views.generic import ListView, DetailView, CreateView
from django.db.models import QuerySet
from .models.models import Cards, Categories
from django.conf import settings
from django.urls import reverse_lazy
from products.forms import AddProductForm, AddCategoryForm
from django.contrib.auth.mixins import LoginRequiredMixin

from products.filters import *


class ProductsView(ListView):
    paginate_by = settings.CATEGORY_PRODUCTS_BATCH_SIZE
    model = Cards
    template_name = "products\\products-listing.html"
    context_object_name = "items"
    _used_model = Categories

    def get_queryset(self):
        category = dashes_to_spaces(self.kwargs.get("category"))
        query_set: QuerySet = Categories.objects.filter(parent=category)

        if not len(query_set):
            min_range = self._get_acceptable_range_price()
            query_set: QuerySet = self.model.objects.filter(category=category, price__gte=min_range)
            self._used_model = self.model

        return query_set.order_by((self.get_ordering() if self._used_model == self.model else "title"))

    def get_context_data(self, *, object_list=None, **kwargs):
        current_context = super().get_context_data(object_list=None, **kwargs)
        self._complement_context(current_context)
        return current_context

    def get_ordering(self):
        return get_ordering_field_from_url_arg(url_arg=self.request.GET.get("price"), field="price")

    def _complement_context(self, current_context: dict) -> None:
        current_context.update({
            "items_is": "categories" if self._used_model == Categories else "cards",
            "filters": "filters" in self.request.GET.keys(),
            "url_args": compile_url_args_for_pagination(
                price=get_url_arg_from_ordering_field(field=self.get_ordering()),
                min_=self._get_acceptable_range_price(),
                filters="filters" in self.request.GET.keys(),
            ),
            "url_args_invert_sorting": compile_url_args_for_pagination(
                price=invert_sorting(get_url_arg_from_ordering_field(field=self.get_ordering())),
                min_=self._get_acceptable_range_price(),
                filters="filters" in self.request.GET.keys(),
            ),
            "max_item_price": Cards.objects.aggregate(Max('price'))["price__max"],
            "min_price": self._get_acceptable_range_price()
        })

    def _get_acceptable_range_price(self):
        try:
            return int(self.request.GET.get("min", 0))
        except:
            return 0


class CardView(DetailView):
    model = Cards
    template_name = "products\\product-details.html"
    context_object_name = "item_info"
    slug_field = "title"
    slug_url_kwarg = "title"

    def get_queryset(self):
        prod_title = self.kwargs.get("title")
        query_set: QuerySet = self.model.objects.filter(title=prod_title)

        return query_set.order_by("title")


class AddProductView(LoginRequiredMixin, CreateView):
    model = Cards
    template_name = "products\\add-product.html"
    form_class = AddProductForm

    def get_success_url(self):
        return reverse_lazy("product-card", kwargs={"title": spaces_to_dashes(self.request.POST["title"])})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(AddProductView, self).form_valid(form=form)


class AddCategoryView(LoginRequiredMixin, CreateView):
    model = Categories
    template_name = "products\\add-category.html"
    form_class = AddCategoryForm
    success_url = reverse_lazy("home")
