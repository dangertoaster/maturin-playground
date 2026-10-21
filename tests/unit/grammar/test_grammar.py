import pytest

from mixedtape.grammar import Statement, apply_statements, matches, parse_selector, walk


class TestParseSelector:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("on amd64", ("on", "amd64")),
            ("to riscv64", ("to", "riscv64")),
            ("  on   arm64  ", ("on", "arm64")),
        ],
    )
    def test_valid(self, text, expected):
        assert parse_selector(text) == expected

    @pytest.mark.parametrize(
        "text", ["", "on", "amd64", "from amd64", "on AMD64", "on amd64 extra"]
    )
    def test_invalid(self, text):
        assert parse_selector(text) is None


class TestMatches:
    def test_matching_on(self):
        assert matches("on amd64", "amd64")

    def test_wrong_verb(self):
        assert not matches("to amd64", "amd64")
        assert matches("to amd64", "amd64", verb="to")

    def test_wrong_arch(self):
        assert not matches("on amd64", "arm64")


class TestWalk:
    @staticmethod
    def _upper(value: str | float | bool | None) -> str:
        # walk() declares a scalar -> Any processor; a plain function keeps
        # the type checker happy where str.upper's overloads confuse it.
        return str(value).upper()

    def test_scalar(self):
        assert walk("x", self._upper) == ["X"]

    def test_list(self):
        assert walk(["a", "b"], self._upper) == ["A", "B"]

    def test_nested(self):
        value = {"on amd64": ["a", {"to arm64": ["b"]}], "else": "c"}
        assert walk(value, self._upper) == ["A", "B", "C"]

    def test_empty_containers(self):
        assert walk([], self._upper) == []
        assert walk({}, self._upper) == []


class TestStatements:
    def test_applies_to(self):
        stmt = Statement(selector="on arm64", body=["foo"])
        assert stmt.applies_to("arm64")
        assert not stmt.applies_to("amd64")

    def test_malformed_selector_never_applies(self):
        assert not Statement(selector="bogus", body=1).applies_to("arm64")

    def test_apply_statements(self):
        statements = [
            Statement("on amd64", "a"),
            Statement("on arm64", "b"),
            Statement("on amd64", "c"),
        ]
        assert apply_statements(statements, "amd64") == ["a", "c"]
        assert apply_statements(statements, "riscv64") == []
