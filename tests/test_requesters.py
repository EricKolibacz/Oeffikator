"""Tests related to the requesters."""
import pytest

from oeffikator.requesters.oeffi_requester import OeffiRequester


def test_for_empty_auth_key():
    """Check if we receive an appropriate warning if the authkey is empty."""
    authkey = ""
    with pytest.raises(ValueError):
        OeffiRequester(authkey)
