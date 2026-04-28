from rest_framework import permissions

from cars.permissions import user_is_admin, user_is_mechanic, user_is_owner


class IsAdminOrOwnsReminderCar(permissions.BasePermission):
    """
    Admins: any reminder.
    Others: only reminders for cars they own (object-level checks).
    List visibility is enforced in get_queryset(); this guards retrieve/update/delete.
    """

    def has_object_permission(self, request, view, obj):
        if user_is_admin(request.user):
            return True
        return obj.car.owner_id == request.user.id


class IsMaintenanceRecordPermission(permissions.BasePermission):
    """
    Admin: full access.

    Mechanic: list/retrieve records they performed; create/update/delete only those
    (enforced here + serializer + queryset).

    Owner: list/retrieve records for their cars only; no create/update/delete.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if user_is_admin(user) or user_is_mechanic(user):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user_is_admin(user):
            return True
        if request.method in permissions.SAFE_METHODS:
            if user_is_mechanic(user):
                return obj.mechanic_id == user.pk
            if user_is_owner(user):
                return obj.car.owner_id == user.pk
            return False
        if user_is_owner(user):
            return False
        if user_is_mechanic(user):
            return obj.mechanic_id == user.pk
        return False
