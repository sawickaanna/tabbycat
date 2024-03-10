from dynamic_preferences.registries import global_preferences_registry
from rest_framework.permissions import BasePermission, SAFE_METHODS

from users.permissions import has_permission


class APIEnabledPermission(BasePermission):
    message = "The API has been disabled on this site."

    def has_permission(self, request, view):
        return global_preferences_registry.manager()['global__enable_api']


class PublicPreferencePermission(BasePermission):

    def has_permission(self, request, view):
        return (request.user and request.user.is_staff) or (
            request.method in SAFE_METHODS and self.get_tournament_preference(view, view.access_operator))

    def get_tournament_preference(self, view, op):
        if type(view.access_preference) is tuple:
            return op(view.tournament.pref(pref) for pref in view.access_preference)
        return op(view.tournament.pref(view.access_preference), view.access_setting)


class PublicIfReleasedPermission(PublicPreferencePermission):

    def has_object_permission(self, request, view, obj):
        return getattr(obj.round, view.round_released_field) == view.round_released_value


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (request.user and request.user.is_staff)


class PerTournamentPermissionRequired(BasePermission):
    def get_required_permissions(self, view):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        return ({
            'list': view.list_permission,
            'create': view.create_permission,
            'retrieve': view.list_permission,
            'update': view.update_permission,
            'partial_update': view.update_permission,
            'destroy': view.destroy_permission,
            'delete_all': view.destroy_permission,
            'add_blank': view.create_permission,
        }).get(view.action, False)

    def has_permission(self, request, view):
        perm = self.get_required_permission(view, request.method)
        return has_permission(request.user, perm, view.tournament)
