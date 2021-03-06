from rlbot.training.training import Fail, Grade
from rlbottraining.grading.grader import Grader, TrainingTickPacket
from typing import Optional, Union
from dataclasses import dataclass
from rlbottraining.history.metric import Metric


class WrongGoalFail(Fail):
    def __repr__(self):
        return f'{super().__repr__()}: Ball went into the wrong goal.'


class BallPassingStrikerFail(Fail):
    def __repr__(self):
        return f'{super().__repr__()}: Ball passed the striker.'


class FailOnTimeout(Grader):
    """Fails the exercise if we take too long."""

    class FailDueToTimeout(Fail):
        def __init__(self, max_duration_seconds):
            self.max_duration_seconds = max_duration_seconds

        def __repr__(self):
            return f'{super().__repr__()}: Timeout: Took longer than {self.max_duration_seconds} seconds.'

    def __init__(self, max_duration_seconds: float):
        self.max_duration_seconds = max_duration_seconds
        self.initial_seconds_elapsed: float = None
        self.measured_duration_seconds: float = None

    def on_tick(self, tick: TrainingTickPacket) -> Optional[Grade]:
        seconds_elapsed = tick.game_tick_packet.game_info.seconds_elapsed
        if self.initial_seconds_elapsed is None:
            self.initial_seconds_elapsed = seconds_elapsed
        self.measured_duration_seconds = seconds_elapsed - self.initial_seconds_elapsed
        if self.measured_duration_seconds > self.max_duration_seconds:
            return self.FailDueToTimeout(self.max_duration_seconds)

    @dataclass(frozen=True)
    class TimeoutMetric(Metric):
        max_duration_seconds: float
        initial_seconds_elapsed: float
        measured_duration_seconds: float

    def get_metric(self) -> Optional[Metric]:
        return FailOnTimeout.TimeoutMetric(
            self.max_duration_seconds,
            self.initial_seconds_elapsed,
            self.measured_duration_seconds,
        )


class FailOnBallPassingStriker(Grader):
    """
    Fails the exercise if the ball passes the striker meaning he missed the shot
    """

    # Prevent false positives which might be caused by two bots touching the ball at basically the same time.
    REQUIRED_CONSECUTIVE_TICKS = 20

    def __init__(self):
        self.consecutive_bad_ticks = 0

    def on_tick(self, tick: TrainingTickPacket) -> Optional[Grade]:
        if tick.game_tick_packet.game_ball.physics.location.y + 500 < tick.game_tick_packet.game_cars[0].physics.location.y:
            self.consecutive_bad_ticks += 1
        else:
            self.consecutive_bad_ticks = 0

        if self.consecutive_bad_ticks >= self.REQUIRED_CONSECUTIVE_TICKS:
            return BallPassingStrikerFail()
