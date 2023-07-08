from django.db import IntegrityError
from django.http.response import HttpResponse
from django.contrib.auth.models import User

from products.models.models import Category, Phones

from lunemarket.lunemarket_tests.tests_presets import *


def create_test_product(test_user: User, test_category: Category = None, **custom_product_fields):
    test_product_fields = get_test_phone_default_fields(
        category=test_category or create_default_test_category(),
        author=test_user
    )

    if custom_product_fields:
        complement_test_product_fields(test_product_fields=test_product_fields, **custom_product_fields)

    return create_test_phone(
        fields=test_product_fields
    )


def complement_test_product_fields(test_product_fields: dict, **new_values) -> None:
    for old_value_key in new_values:
        if old_value_key in test_product_fields.keys():
            test_product_fields[old_value_key] = new_values[old_value_key]


def get_test_phone_default_fields(category: Category, author: User) -> dict:
    test_phone_default_fields = TEST_PHONE_DEFAULT_FIELDS.copy()
    test_phone_default_fields["category"], test_phone_default_fields["author"] = category, author

    return test_phone_default_fields


def create_test_phone(fields: dict = None) -> Phones:
    new_test_phone = Phones(**fields)
    new_test_phone.save()

    return new_test_phone


def create_test_user() -> User:
    new_user = User(username=TEST_USER_DEFAULT_USERNAME,
                    email=TEST_USER_DEFAULT_EMAIL,
                    password=TEST_USER_DEFAULT_PASSWORD)

    try:
        if User.objects.all().exists():
            new_user.username = TEST_SECOND_USER_DEFAULT_USERNAME

    except User.DoesNotExist:
        pass

    finally:
        new_user.save()

    return new_user


def create_default_test_category() -> Category:
    test_category = Category(**TEST_CATEGORY_DEFAULT_FIELDS)
    test_category.save()

    return test_category


def response_is_redirect(response: HttpResponse) -> bool:
    return response.status_code // 100 == 3
