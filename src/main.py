import click
import enum
from launcher.tk.tk_launcher import ChessTkinterLauncher
from launcher.pg.pg_launcher import ChessPygameLauncher, SinglePlayerGameType


class AppType(enum.Enum):
    LAUNCHER = enum.auto()
    CLIENT = enum.auto()
    SERVER = enum.auto()
    PLAYER_V_PLAYER = enum.auto()


@click.command()
@click.option('--app_type', default=AppType.LAUNCHER.name, help='select what to launch. LAUNCHER, CLIENT, '
                                                                'SERVER or LOCAL')
@click.option('--server_ip', default='127.0.0.1', help='set the server ip address default = 127.0.0.1')
@click.option('--scale', default=3.5, help='size of chess game, lower than 3.5 will cause the fonts to be unclear')
@click.option('--theme_id', default=1, help='game theme, possible ids (1 - 4), (-1 for random theme)')
@click.option('--pieces_asset', default='RANDOM', help='piece assets, possible names SMALL, LARGE, RANDOM')
@click.option(
    '--timer',
    default='BLITZ_5_0',
    help='''
    choose timer settings, custom setting format "time increment" (time-minutes, increment-seconds)
    e.g "15 0"\n 
    possible timers:\n
    BULLET_1_0 BULLET_1_1 BULLET_2_1\n
    BLITZ_3_0 BLITZ_3_2 BLITZ_5_0\n
    RAPID_15_10 RAPID_30_0 RAPID_60_0\n
    '''
)
def start_app(
        app_type: str,
        server_ip: str,
        scale: float,
        theme_id: int,
        pieces_asset: str,
        timer: str
) -> None:
    app_type: AppType = AppType[app_type]
    pg_launcher: ChessPygameLauncher = ChessPygameLauncher()
    tk_launcher: ChessTkinterLauncher = ChessTkinterLauncher()

    pg_launcher.update_config(
        update_config=False,
        theme_id=theme_id,
        scale=scale,
        asset_name=pieces_asset,
        timer_config_name=timer,
        server_ip=server_ip
    )

    if app_type is AppType.LAUNCHER:
        tk_launcher.mainloop()

    elif app_type is AppType.SERVER:
        pg_launcher.run_local_server()

    elif app_type is AppType.PLAYER_V_PLAYER:
        pg_launcher.launch_single_player(SinglePlayerGameType.HUMAN_VS_HUMAN)

    elif app_type is AppType.CLIENT:
        pg_launcher.launch_multi_player_client()


if __name__ == "__main__":
    start_app()