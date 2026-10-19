import pytest

from mixedtape.platform import Arch, filter_arches


class TestArch:
    def test_from_deb_known(self):
        assert Arch.from_deb("amd64") is Arch.AMD64

    def test_from_deb_unknown(self):
        with pytest.raises(ValueError, match="unknown architecture: 'sparc'"):
            Arch.from_deb("sparc")

    def test_is_str_enum(self):
        assert Arch.ARM64 == "arm64"


class TestFilterArches:
    def test_filters_unsupported(self):
        result = filter_arches(["amd64", "arm64"], supported={Arch.AMD64})
        assert result == [Arch.AMD64]

    def test_drops_unknown_silently(self):
        result = filter_arches(["amd64", "sparc"], supported={Arch.AMD64})
        assert result == [Arch.AMD64]

    def test_preserves_order_and_dedupes(self):
        result = filter_arches(
            ["arm64", "amd64", "arm64"], supported={Arch.AMD64, Arch.ARM64}
        )
        assert result == [Arch.ARM64, Arch.AMD64]

    def test_empty(self):
        assert filter_arches([], supported=set()) == []
