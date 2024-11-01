import pytest

from tf2mon.cli import main


def test_list_con_logfile() -> None:
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
def test_config_files(config_file: str, expected: list[str]) -> None:

    print()
    try:
        main(["-v", "--config", config_file, "--print-config"])
    except SystemExit as err:
        print(f"err: {err}")
        # assert err.value.code == 0
        print(f"Expected: {expected}")
    else:
        pytest.fail("didn't exit")


def test_console_log() -> None:
    pass
