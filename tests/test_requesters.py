"""Tests related to the requesters."""
import pytest

from oeffikator.requesters.oeffi_requester import OeffiRequester


def test_for_empty_auth_key():
    """Check if we receive an appropriate warning if the authkey is empty."""
    authkey = ""
    with pytest.raises(ValueError):
        OeffiRequester(authkey)


def test_for_none_auth_key():
    """Check if we receive an appropriate warning if the authkey is None."""
    authkey = None
    with pytest.raises(ValueError):
        OeffiRequester(authkey)
