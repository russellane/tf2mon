from pathlib import Path

from tf2mon.steamweb import SteamWebAPI

DBFILE = Path.home() / ".cache" / "tf2mon" / "steamplayers.db"


def test_steam():
    api = SteamWebAPI(webapi_key=None, dbpath=DBFILE)
    api.connect()
    for player in api.players():
        print(player)

    # import pandas as pd
    # df = pd.read_sql_query("SELECT * from steamplayers", api._con)  # noqa
    # with pd.option_context("display.max_rows", None, "display.max_columns", None):
    #     print(df)
