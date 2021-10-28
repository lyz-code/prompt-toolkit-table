"""Test the implementation of the Table widget."""

import pytest
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous

from prompt_toolkit_table import Table

from ..conftest import DictData


@pytest.mark.skip("Not yet")
class TestBindings:
    """Test the bindings of the Table."""

    def test_table_default_bindings(self, dict_data: DictData) -> None:
        """
        Given: A Table object
        When: initialized without any binding
        Then: The default bindings are set.
        """
        result = Table(dict_data)

        assert result.key_bindings is not None
        bindings = result.key_bindings.bindings
        assert len(bindings) == 2
        for binding in bindings:
            if binding.keys == ("j",):
                assert binding.handler == focus_next
            elif binding.keys == ("k",):
                assert binding.handler == focus_previous

    def test_table_merges_bindings(self, dict_data: DictData) -> None:
        """
        Given: A Table object and some new bindings
        When: initialized with the new bindings
        Then: the default bindings are overwritten

        In prompt_toolkit the merge_key_bindings doesn't overwrite the existing
        bindings, instead it adds them to the end and I guess the `eager` will take
        preference.
        """
        new_bindings = KeyBindings()
        new_bindings.add("j", eager=True)(focus_previous)

        result = Table(dict_data, key_bindings=new_bindings)

        assert result.key_bindings is not None
        bindings = result.key_bindings.bindings
        assert len(bindings) == 3
        for binding in bindings:
            if binding.keys == ("j",) and not binding.eager():
                assert binding.handler == focus_next
            elif binding.keys == ("j",) and binding.eager():
                assert binding.handler == focus_previous
            elif binding.keys == ("k",):
                assert binding.handler == focus_previous
