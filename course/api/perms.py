from rest_framework.permissions import BasePermission


class IsEnrolled(BasePermission):
    """ 
        A custom permission for course class that handles permission on each object
        obj represents the course object
    """
    def has_object_permission(self, request, view, obj):
        res = obj.students.filter(id=request.user.id).exists()
        return res
    
    def has_permission(self, request, view):
        return super().has_permission(request, view)


