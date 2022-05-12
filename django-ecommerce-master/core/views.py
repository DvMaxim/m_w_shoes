from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.utils.decorators import method_decorator
from .forms import Product, Contact, AccountInfo
from .models import Item, OrderItem, Order, ContactInfo
from django.shortcuts import reverse
from django.contrib.auth.models import User


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


def about(request):
    return render(request, 'about.html')


class HomeView(ListView):
    model = Item
    template_name = "home.html"

    def get(self, *args, **kwargs):
        sorted_items = Item.objects.all().order_by('data_added')
        most_popular_item = Item.objects.all().order_by('prioritize')[::-1][0]
        context = {
            'sorted_items': sorted_items[:3],
            'most_popular_item': most_popular_item
        }

        return render(self.request, self.template_name, context)


start_main_category = None
start_sub_category = None


class ProductsView(ListView):
    model = Item
    paginate_by = 4
    template_name = "products.html"
    main_category = start_main_category
    sub_menu = start_sub_category

    def get_queryset(self):

        if ('main_id' in self.kwargs) and ('sub_id' in self.kwargs):
            self.sub_menu = self.kwargs['sub_id']
            if self.main_category:
                object_list = Item.objects.filter(owner=self.main_category, category=self.sub_menu)
            else:
                if self.sub_menu != 'all':
                    object_list = Item.objects.filter(category=self.sub_menu)
                else:
                    object_list = Item.objects.all()

        elif 'main_id' in self.kwargs:
            self.main_category = self.kwargs['main_id']

            if self.sub_menu:

                if self.main_category != 'A':
                    object_list = Item.objects.filter(owner=self.main_category, category=self.sub_menu)
                else:
                    object_list = Item.objects.all(category=self.sub_menu)

            else:
                if self.main_category != 'A':
                    object_list = Item.objects.filter(owner=self.main_category)
                else:
                    object_list = Item.objects.all()

        else:
            object_list = Item.objects.all()

        global start_main_category, start_sub_category
        start_main_category = self.main_category
        start_sub_category = self.sub_menu
        return object_list


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

    def get(self, *args, **kwargs):
        slug = self.kwargs['slug']
        item = Item.objects.get(slug=slug)
        product_form = Product()
        item.prioritize += 1
        item.save()
        context = {
            'item': item,
            'form': product_form,
            'sub_images': item.sub_images
        }

        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        slug = self.kwargs['slug']
        form = Product(self.request.POST)
        if form.is_valid():
            count = form.cleaned_data['count']
            if count <= 0:
                messages.info(self.request,
                              "Кажется вы ошиблись с количеством. Пожалуйста, проверьте еще раз и повторите ввод.")
                return reverse("core:product", kwargs={
                    'slug': slug
                })
            else:
                if 'add_cart' in form.data:
                    return redirect("core:add-to-cart", slug=slug, count=count)
                elif 'delete_cart' in form.data:
                    return redirect("core:remove-from-cart", slug=slug, count=count)


class OrderSummaryView(LoginRequiredMixin, View):
    template_name = "order_summary.html"

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order}
            return render(self.request, self.template_name, context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "У вас нет активного заказа!")
            return redirect("/")


@login_required
def add_to_cart(request, slug, count):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += count
            order_item.save()
            messages.info(request, "Количество товара в заказе успешно обновлено")
            return redirect("core:product", slug=slug)
        else:
            order_item.quantity = count
            order_item.save()
            order.items.add(order_item)
            messages.info(request, "Товар был успешно добавлен в корзину.")
            return redirect("core:product", slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date, ordered=False)
        order_item.quantity = count
        order_item.save()
        order.items.add(order_item)
        messages.info(request, "Товар был успешно добавлен в корзину.")
        return redirect("core:product", slug=slug)


@login_required
def add_single_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]

            order_item.quantity += 1
            order_item.save()
            # messages.info(request, "Количество данного товара было успешно обновлено.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Этот товар не в вашей корзине")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "У вас нет активного заказа !")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            # messages.info(request, "Количество данного товара было успешно обновлено.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Этот товар не в вашей корзине")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "У вас нет активного заказа !")
        return redirect("core:product", slug=slug)


@login_required
def remove_from_cart(request, slug, count):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > count:
                order_item.quantity = order_item.quantity - count
                order_item.save()
                messages.info(request, "Указанное количество элементов товара было успешно удалено из корзины.")
            else:
                order.items.remove(order_item)
                order_item.delete()
                messages.info(request, "Нужное количество товара было успешно удалено из корзины.")
            return redirect("core:product", slug=slug)
        else:
            messages.info(request, "Удаление товара невозможно, так как он не находиться в вашей корзине.")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Заказа с данным товаром не существует. "
                               "Пожалуйста, оформите заказ, чтобы иметь возможность удаления элементов.")
        return redirect("core:product", slug=slug)


@login_required
def remove_all_items_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            # messages.info(request, "Все элементы данного товара успешно удалены из корзины.")
            return redirect("core:order-summary")
        else:
            # just for some extra security
            messages.info(request, "Этот товар не в вашей корзине")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "У вас нет активного заказа !")
        return redirect("core:product", slug=slug)


@login_required
def confirm_offer(request):
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        letter = "Ваш заказ:\n\n"
        for order_item in list(order.items.all()):
            order_item.ordered = True
            order_item.save()
            letter += f"{order_item.item.title} в количестве {order_item.quantity}\n"
        order.ordered = True
        order.save()
        letter += f"\nСумма заказа: ${order.get_total()}.\n\n" \
                  f"В данный момент ваш заказ находится в обработке. " \
                  f"Пожалуйста, подождите пока с вами свяжутся для осуществления оплаты.\n\n" \
                  f"Спасибо, что выбирайте нас!"

        send_mail(f'Сообщение от {request.user}', letter, settings.DEFAULT_CONTACT_EMAIL, [request.user.email],
                  fail_silently=False)

        return render(request, "order_confirmed.html")

    else:
        messages.info(request, "Невозможно подтвердить заказ! Ваша корзина пуста!\n"
                               "Пожалуйста,выберите элементы для заказа и продолжите работу.")
        return redirect("core:products")


@method_decorator(login_required, name='dispatch')
class ContactView(View):
    model = ContactInfo
    template_name = "contact.html"

    def get(self, *args, **kwargs):

        form = Contact()
        context = {
            'form': form
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        form = Contact(self.request.POST)
        if form.is_valid():
            letter = form.cleaned_data['letter']
            destination_email = form.cleaned_data['destination_email']
            new_contact = ContactInfo.objects.create(user=self.request.user, letter=letter,
                                                     destination_email=destination_email)
            send_mail(f'Сообщение от {new_contact.user}',
                      new_contact.letter, new_contact.user.email, [destination_email], fail_silently=False)
            messages.info(self.request, "Сообщение успешно отправлено.")
            return redirect("core:contact")
        else:
            messages.info(self.request, "Во введенных вами данных допущена ошибка. Пожалуйста, решите проблему и"
                                        "повторите отправку.")
            return redirect("core:contact")


class AccountInfoView(LoginRequiredMixin, View):
    model = User
    template_name = "account_info.html"

    def get(self, *args, **kwargs):
        user = get_object_or_404(self.model, username=self.request.user)
        orders = list(Order.objects.filter(user=user, ordered=True))
        form = AccountInfo(initial={'user_email': user.email,
                                    'first_name': user.first_name,
                                    'last_name': user.last_name})
        context = {
            'form': form,
            'orders': orders
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        form = AccountInfo(self.request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user_email = form.cleaned_data['user_email']

            user = get_object_or_404(self.model, username=self.request.user)

            user.email = user_email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            messages.info(self.request, "Данные успешно обновлены.")
            return redirect("core:account-info")
        else:
            messages.info(self.request, "Во введенных вами данных допущена ошибка. Пожалуйста, решите проблему и"
                                        "повторите отправку.")
            return redirect("core:account-info")
