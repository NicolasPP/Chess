import dataclasses


@dataclasses.dataclass
class TimerConfig:
    # seconds
    time: float
    increment: float


class DefaultConfigs:
    # Bullet time controls refer to any time control that is faster than three minutes per player.
    BULLET_1_0 = TimerConfig(1 * 60, 0)
    BULLET_1_1 = TimerConfig(1 * 60, 1)
    BULLET_2_1 = TimerConfig(2 * 60, 1)

    # Blitz time controls are between three and ten minutes per player.
    BLITZ_3_0 = TimerConfig(3 * 60, 0)
    BLITZ_3_2 = TimerConfig(3 * 60, 2)
    BLITZ_5_0 = TimerConfig(5 * 60, 0)

    # Rapid time controls are any time controls that are longer than ten minutes per player.
    RAPID_15_10 = TimerConfig(15 * 60, 10)
    RAPID_30_0 = TimerConfig(30 * 60, 0)
    RAPID_60_0 = TimerConfig(60 * 60, 0)

    @staticmethod
    def get_timer_config(name: str) -> TimerConfig:
        if is_custom_name(name):
            time, increment = name.split()
            return TimerConfig(float(time) * 60, float(increment))

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


def is_custom_name(name: str) -> bool:
    if not name.__contains__(" "): return False
    if len(name.split()) != 2: return False
    time, increment = name.split()
    if not time.isnumeric() or not increment.isnumeric(): return False
    return True
