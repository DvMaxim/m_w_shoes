from django.test import TestCase

from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from .models import ContactInfo, Order, Item


class ContactInfoModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.contacts = ContactInfo.objects.all()

    def setUp(self):
        self.contacts = ContactInfo.objects.all()

    def test_contact_has_letter_oversize(self):
        fail_contacts = [contact for contact in self.contacts if len(contact.letter) > 3000]
        print("\nTest case: test_contact_has_letter_oversize.")

        fail_message = "Incorrect contacts:\n"

        if fail_contacts:
            for contact in fail_contacts:
                fail_message += f"User: {contact.user}; Email destination: {contact.destination_email}.\n"

        self.assertFalse(fail_contacts, fail_message)

        print("Success!")


class OrderModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.orders = Order.objects.all()

    def setUp(self):
        self.orders = Order.objects.all()

    def is_any_ready_orders(self):
        print("\nTest case: is_any_ready_orders.")
        ready_orders = self.orders.filter(ordered=True)

        self.assertTrue(ready_orders, "Impossible to process orders. No ordered ones' found.")

        print("Success!")

    def is_any_active_orders(self):
        print("\nTest case: is_any_active_orders.")
        ready_orders = self.orders.filter(ordered=False)

        self.assertTrue(ready_orders, "Impossible to work with orders. No active ones' found.")

        print("Success!")


class ItemModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.items = Item.objects.all()

    def setUp(self):
        self.items = Item.objects.all()

    def test_is_items_exist(self):
        print("\nTest case: test_is_items_exist.")
        self.assertTrue(self.items, "Impossible to display items. No active ones' found.")

    def test_title(self):
        print("\nTest case: test_title.")
        for item in self.items:
            self.assertIsInstance(item.title, str, "Error! Title of the item must be string.")

    def test_price(self):
        print("\nTest case: test_price.")
        for item in self.items:
            self.assertIsInstance(item.title, int, "Error! Price of the item must be float.")

    def test_data_added(self):
        print("\nTest case: test_data_added.")
        for item in self.items:
            self.assertIsInstance(item.data_added,
                                  datetime, "Error! Added data of the item must be float.")


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = User.objects.all()

    def setUp(self):
        self.users = User.objects.all()

    def test_duplicate_login(self):
        duplicate_login_users = []

        for i in range(len(self.users)):
            init_login = self.users[i].username
            if len(User.objects.filter(username=init_login)) > 1:
                if self.users[i].username not in duplicate_login_users:
                    duplicate_login_users.append(self.users[i].username)

        message = "Users with duplicate logins:\n\n"

        for username in duplicate_login_users:
            message += f"User: {username}.\n"

        self.assertFalse(duplicate_login_users, message)




