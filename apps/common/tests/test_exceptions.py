"""
Jednotkové testy pro apps/common exceptions.

Pokrývá:
- BusinessError (400)
- NotFoundError (404)
- PermissionDeniedError (403)
"""

import pytest
from rest_framework import status

from apps.common.exceptions import BusinessError, NotFoundError, PermissionDeniedError

pytestmark = pytest.mark.unit


class TestBusinessError:
    """Testy pro BusinessError."""

    def test_status_code(self):
        """Test: BusinessError má status 400."""
        err = BusinessError()
        assert err.status_code == status.HTTP_400_BAD_REQUEST

    def test_default_detail(self):
        """Test: BusinessError má výchozí hlášku."""
        err = BusinessError()
        assert err.default_detail != ""

    def test_custom_detail(self):
        """Test: BusinessError přijímá vlastní zprávu."""
        err = BusinessError("Vlastní chyba")
        assert "Vlastní chyba" in str(err.detail)

    def test_is_exception(self):
        """Test: BusinessError je výjimka."""
        assert issubclass(BusinessError, Exception)

    def test_can_be_raised_and_caught(self):
        """Test: Lze vyhodit a zachytit."""
        with pytest.raises(BusinessError, match="Chyba"):
            raise BusinessError("Chyba")

    def test_default_code(self):
        """Test: Výchozí kód je business_error."""
        err = BusinessError()
        assert err.default_code == "business_error"


class TestNotFoundError:
    """Testy pro NotFoundError."""

    def test_status_code(self):
        """Test: NotFoundError má status 404."""
        err = NotFoundError()
        assert err.status_code == status.HTTP_404_NOT_FOUND

    def test_default_detail(self):
        """Test: NotFoundError má výchozí hlášku."""
        err = NotFoundError()
        assert err.default_detail != ""

    def test_custom_detail(self):
        """Test: NotFoundError přijímá vlastní zprávu."""
        err = NotFoundError("Nenalezeno")
        assert "Nenalezeno" in str(err.detail)

    def test_is_exception(self):
        """Test: NotFoundError je výjimka."""
        assert issubclass(NotFoundError, Exception)

    def test_can_be_raised_and_caught(self):
        """Test: Lze vyhodit a zachytit."""
        with pytest.raises(NotFoundError, match="Objekt chybí"):
            raise NotFoundError("Objekt chybí")

    def test_default_code(self):
        """Test: Výchozí kód je not_found."""
        err = NotFoundError()
        assert err.default_code == "not_found"


class TestPermissionDeniedError:
    """Testy pro PermissionDeniedError."""

    def test_status_code(self):
        """Test: PermissionDeniedError má status 403."""
        err = PermissionDeniedError()
        assert err.status_code == status.HTTP_403_FORBIDDEN

    def test_default_detail(self):
        """Test: PermissionDeniedError má výchozí hlášku."""
        err = PermissionDeniedError()
        assert err.default_detail != ""

    def test_custom_detail(self):
        """Test: PermissionDeniedError přijímá vlastní zprávu."""
        err = PermissionDeniedError("Zakázáno")
        assert "Zakázáno" in str(err.detail)

    def test_is_exception(self):
        """Test: PermissionDeniedError je výjimka."""
        assert issubclass(PermissionDeniedError, Exception)

    def test_can_be_raised_and_caught(self):
        """Test: Lze vyhodit a zachytit."""
        with pytest.raises(PermissionDeniedError):
            raise PermissionDeniedError("Přístup odepřen")

    def test_default_code(self):
        """Test: Výchozí kód je permission_denied."""
        err = PermissionDeniedError()
        assert err.default_code == "permission_denied"


class TestExceptionHierarchy:
    """Testy hierarchie výjimek."""

    def test_all_inherit_from_api_exception(self):
        """Test: Všechny výjimky dědí z APIException (DRF)."""
        from rest_framework.exceptions import APIException

        for exc_class in (BusinessError, NotFoundError, PermissionDeniedError):
            assert issubclass(exc_class, APIException)

    def test_different_status_codes(self):
        """Test: Každá výjimka má jiný status kód."""
        codes = {BusinessError().status_code, NotFoundError().status_code, PermissionDeniedError().status_code}
        assert len(codes) == 3
