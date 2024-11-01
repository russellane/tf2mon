import sys
from subprocess import run

import pytest

from tf2mon.cli import main


def test_main() -> None:

    def _main() -> None:
        run(["python", "-m", "tf2mon", "--version"], check=True)
        sys.exit(0)

    with pytest.raises(SystemExit) as err:
        _main()
    assert err.value.code == 0


def test_version() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--version"])
    assert err.value.code == 0


def test_help() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--help"])
    assert err.value.code == 0


def test_md_help() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--md-help"])
    assert err.value.code == 0


def test_long_help() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--long-help"])
    assert err.value.code == 2


def test_bogus_option() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--bogus-option"])
    assert err.value.code == 2


def test_print_config() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--print-config"])
    assert err.value.code == 0


def test_print_url() -> None:
    with pytest.raises(SystemExit) as err:
        main(["--print-url"])
    assert err.value.code == 0
