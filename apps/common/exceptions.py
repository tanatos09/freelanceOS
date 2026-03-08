"""
Custom exceptions for business logic.

Use these instead of ValueError/generic exceptions in services.
They are automatically converted to proper HTTP responses by DRF.
"""
from rest_framework import status
from rest_framework.exceptions import APIException


class BusinessError(APIException):
    """Base exception for business rule violations (400)."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Chyba v business logice.'
    default_code = 'business_error'


class NotFoundError(APIException):
    """Resource not found within the current scope (404)."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Objekt nenalezen.'
    default_code = 'not_found'


class PermissionDeniedError(APIException):
    """User lacks permission for the action (403)."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Nemáte oprávnění k této akci.'
    default_code = 'permission_denied'
