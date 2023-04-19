import dataclasses


@dataclasses.dataclass
class TimerConfig:
    # seconds
    time: float
    increment: float


class DefaultConfigs:
    # Bullet time controls refer to any time control that is faster than three minutes per player.
    BULLET_1 = TimerConfig(1 * 60, 0)
    BULLET_1_1 = TimerConfig(1 * 60, 1)
    BULLET_2_1 = TimerConfig(2 * 60, 1)

    # Blitz time controls are between three and ten minutes per player.
    BLITZ_3 = TimerConfig(3 * 60, 0)
    BLITZ_3_2 = TimerConfig(3 * 60, 2)
    BLITZ_5 = TimerConfig(5 * 60, 0)

    # Rapid time controls are any time controls that are longer than ten minutes per player.
    RAPID_15_10 = TimerConfig(15 * 60, 10)
    RAPID_30 = TimerConfig(30 * 60, 0)
    RAPID_60 = TimerConfig(60 * 60, 0)
