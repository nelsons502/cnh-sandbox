def minutes_between(end_minute: int, next_start_minute: int) -> int:
    return next_start_minute - end_minute


def is_back_to_back(end_minute: int, next_start_minute: int, buffer_minutes: int = 10) -> bool:
    return minutes_between(end_minute, next_start_minute) > buffer_minutes
