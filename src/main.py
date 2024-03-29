import enum

import click
from chess_engine.movement.piece_movement import PieceMovement

from config.logging_manager import AppLoggers
from config.logging_manager import LoggingManager
from config.logging_manager import LoggingOut
from config.tk_config import LOCAL_CHESS_DB_INFO
from config.user_config import UserConfig
from database.chess_db import DataBaseInfo
from launcher.pg.pg_launcher import ChessPygameLauncher
from launcher.pg.pg_launcher import SinglePlayerGameType
from launcher.tk.tk_launcher import ChessTkinterLauncher
from network.server.chess_server import ChessServer


class AppType(enum.Enum):
    LAUNCHER = enum.auto()
    SERVER = enum.auto()
    PLAYER_V_PLAYER = enum.auto()


@click.command()
@click.option('--server_log_stdout', is_flag=True, help='set server logging to stdout')
@click.option('--client_log_stdout', is_flag=True, help='set client logging to stdout')
@click.option('--bot_log_stdout', is_flag=True, help='set bot logging to stdout')
@click.option('--database_log_stdout', is_flag=True, help='set database logging to stdout')
@click.option('--launcher_log_stdout', is_flag=True, help='set launcher logging to stdout')
@click.option('--app_type', default=AppType.LAUNCHER.name, help='select what to launch. LAUNCHER, CLIENT, '
                                                                'SERVER or LOCAL')
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
        server_log_stdout: bool,
        client_log_stdout: bool,
        bot_log_stdout: bool,
        database_log_stdout: bool,
        launcher_log_stdout: bool,
        app_type: str,
        scale: float,
        theme_id: int,
        pieces_asset: str,
        timer: str
) -> None:
    LoggingManager.load_configs()
    app: AppType = AppType[app_type]
    database_info: DataBaseInfo = DataBaseInfo(*LOCAL_CHESS_DB_INFO)
    ChessServer.set_database_info(database_info)

    UserConfig.get().update_config(
        update_local_config=False,
        theme_id=theme_id,
        scale=scale,
        asset_name=pieces_asset,
        timer_config_name=timer,
    )

    if server_log_stdout:
        LoggingManager.configure(AppLoggers.SERVER, out=LoggingOut.STDOUT)

    if client_log_stdout:
        LoggingManager.configure(AppLoggers.CLIENT, out=LoggingOut.STDOUT)

    if bot_log_stdout:
        LoggingManager.configure(AppLoggers.BOT, out=LoggingOut.STDOUT)

    if database_log_stdout:
        LoggingManager.configure(AppLoggers.DATABASE, out=LoggingOut.STDOUT)

    if launcher_log_stdout:
        LoggingManager.configure(AppLoggers.ONLINE_LAUNCHER, out=LoggingOut.STDOUT)

    if app is AppType.LAUNCHER:
        UserConfig.get().load_user_config()
        ChessTkinterLauncher(database_info).mainloop()

    elif app is AppType.SERVER:
        PieceMovement.load()
        ChessServer.get().start()
        ChessServer.get().run()

    elif app is AppType.PLAYER_V_PLAYER:
        ChessPygameLauncher.get().launch_single_player(SinglePlayerGameType.HUMAN_VS_HUMAN)


if __name__ == "__main__":
    start_app()
