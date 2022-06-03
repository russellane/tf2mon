import pytest

from tf2mon.cli import main


def test_version():
    with pytest.raises(SystemExit) as err:
        main(["--version"])
    assert err.value.code == 0


def test_help():
    with pytest.raises(SystemExit) as err:
        main(["--help"])
    assert err.value.code == 0


def test_md_help():
    with pytest.raises(SystemExit) as err:
        main(["--md-help"])
    assert err.value.code == 0


def test_long_help():
    with pytest.raises(SystemExit) as err:
        main(["--long-help"])
    assert err.value.code == 2


def test_bogus_option():
    with pytest.raises(SystemExit) as err:
        main(["--bogus-option"])
    assert err.value.code == 2


def test_print_config():
    with pytest.raises(SystemExit) as err:
        main(["--print-config"])
    assert err.value.code == 0


def test_print_url():
    with pytest.raises(SystemExit) as err:
        main(["--print-url"])
    assert err.value.code == 0


def test_debug():
    with pytest.raises(SystemExit) as err:
        main(["-X"])
    assert err.value.code == 0


def test_list_con_logfile():
    with pytest.raises(SystemExit) as err:
        main(["--list-con-logfile"])
    assert err.value.code == 0


@pytest.mark.parametrize(
    ("config_file", "expected"),
    [
        # (
        #     "/dev/null",
        #     str(
        #         "[tf2mon]\n"
        #         'config-file = "/dev/null"\n'
        #         'tf2_install_dir = "/home/russel/SteamLibrary/'
        #         'steamapps/common/Team Fortress 2/tf"\n'
        #         'con_logfile = "console.log"\n',
        #     ),
        # ),
        # ("tests/fixtures/file1.toml", None),
        # ("tests/fixtures/file2.toml", None),
        # ("tests/fixtures/file3.toml", None),
    ],
)
def test_config_files(config_file, expected):

    print()
    try:
        main(["-v", "--config", config_file, "--print-config"])
    except SystemExit as err:
        print(f"err: {err}")
        # assert err.value.code == 0
        print(f"Expected: {expected}")
    else:
        pytest.fail("didn't exit")
