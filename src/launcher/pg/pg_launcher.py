from launcher.pg.offline_launcher import OfflineLauncher
from launcher.pg.online_launcher import OnlineLauncher
from chess.asset.chess_assets import PieceSetAssets, Themes, ChessTheme, PieceSetAsset
from chess.timer.timer_config import TimerConfig
from server import Server


class PygameChessLauncher:

    def __init__(self):
        self.theme: ChessTheme = Themes.PLAIN1
        self.scale: float = 3.5
        self.piece_set: PieceSetAsset = PieceSetAssets.SIMPLE16x16
        self.timer_config: TimerConfig = TimerConfig(60 * 10, 0)
        self.server_ip: str = '127.0.0.1'
        self.multi_player: OnlineLauncher = OnlineLauncher()
        self.single_player: OfflineLauncher = OfflineLauncher()
        self.server: Server = Server(self.timer_config)
        self.is_running: bool = False

    def get_is_running(self) -> bool:
        return self.is_running

    def launch_single_player(self) -> None:
        if self.get_is_running(): return
        self.is_running = True
        self.single_player.launch(self.theme, self.scale, self.piece_set, self.timer_config)
        self.is_running = False

    def launch_multi_player_client(self) -> None:
        if self.get_is_running(): return
        self.is_running = True
        self.multi_player.launch(self.server_ip, self.theme, self.scale, self.piece_set)
        self.is_running = False

    def run_local_server(self) -> None:
        if self.get_is_running(): return
        self.is_running = True
        self.server.run()
        self.is_running = False
