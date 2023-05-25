from django.contrib.auth.mixins import UserPassesTestMixin


def admin_test(user):
    return user.is_active and user.is_superuser


class AdminTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_active and self.request.user.is_superuser