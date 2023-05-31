from __future__ import annotations


class TimerConfig:

    @staticmethod
    def get_timer_config(name: str) -> TimerConfig:
        if is_custom_name(name):
            time, increment = name.split()
            return TimerConfig(float(time) * 60, float(increment), "CUSTOM")

        elif name == "BULLET_1_0":
            return DefaultConfigs.BULLET_1_0

        elif name == "BULLET_1_1":
            return DefaultConfigs.BULLET_1_1

        elif name == "BULLET_2_1":
            return DefaultConfigs.BULLET_2_1

        elif name == "BLITZ_3_0":
            return DefaultConfigs.BLITZ_3_0

        elif name == "BLITZ_3_2":
            return DefaultConfigs.BLITZ_3_2

        elif name == "BLITZ_5_0":
            return DefaultConfigs.BLITZ_5_0

        elif name == "RAPID_15_10":
            return DefaultConfigs.RAPID_15_10

        elif name == "RAPID_30_0":
            return DefaultConfigs.RAPID_30_0

        elif name == "RAPID_60_0":
            return DefaultConfigs.RAPID_60_0

        else:
            raise Exception(f'timer: {name} not recognised')

    def __init__(self, time: float, increment: float, name: str) -> None:
        # seconds
        self.time: float = time
        self.increment: float = increment
        self.name: str = name

    def get_value_str(self) -> str:
        return f"{self.time} {self.increment}"

    def get_name(self) -> str:
        return self.name


def is_custom_name(name: str) -> bool:
    if not name.__contains__(" "): return False
    if len(name.split()) != 2: return False
    time, increment = name.split()
    if not time.isnumeric() or not increment.isnumeric(): return False
    return True


class DefaultConfigs:
    # Bullet time controls refer to any time control that is faster than three minutes per player.
    BULLET_1_0: TimerConfig = TimerConfig(1 * 60, 0, "BULLET_1_0")
    BULLET_1_1: TimerConfig = TimerConfig(1 * 60, 1, "BULLET_1_1")
    BULLET_2_1: TimerConfig = TimerConfig(2 * 60, 1, "BULLET_2_1")

    # Blitz time controls are between three and ten minutes per player.
    BLITZ_3_0: TimerConfig = TimerConfig(3 * 60, 0, "BLITZ_3_0")
    BLITZ_3_2: TimerConfig = TimerConfig(3 * 60, 2, "BLITZ_3_2")
    BLITZ_5_0: TimerConfig = TimerConfig(5 * 60, 0, "BLITZ_5_0")

    # Rapid time controls are any time controls that are longer than ten minutes per player.
    RAPID_15_10: TimerConfig = TimerConfig(15 * 60, 10, "RAPID_15_10")
    RAPID_30_0: TimerConfig = TimerConfig(30 * 60, 0, "RAPID_30_0")
    RAPID_60_0: TimerConfig = TimerConfig(60 * 60, 0, "RAPID_60_0")
