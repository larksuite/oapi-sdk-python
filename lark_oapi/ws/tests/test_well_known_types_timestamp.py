import datetime
import time
import warnings

from lark_oapi.ws.pb.google.protobuf import timestamp_pb2


def test_timestamp_get_current_time_no_deprecation_warning():
    """GetCurrentTime must not emit DeprecationWarning (issue #145)."""
    ts = timestamp_pb2.Timestamp()
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        ts.GetCurrentTime()
    assert abs(ts.ToSeconds() - time.time()) < 5


def test_timestamp_from_to_datetime_roundtrip_naive():
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(datetime.datetime(2024, 1, 2, 3, 4, 5, 123456))
    dt = ts.ToDatetime()
    assert dt == datetime.datetime(2024, 1, 2, 3, 4, 5, 123456)


def test_timestamp_from_to_datetime_roundtrip_aware():
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(
        datetime.datetime(2024, 1, 2, 3, 4, 5, 123456, tzinfo=datetime.timezone.utc)
    )
    dt = ts.ToDatetime(tzinfo=datetime.timezone.utc)
    assert dt == datetime.datetime(
        2024, 1, 2, 3, 4, 5, 123456, tzinfo=datetime.timezone.utc
    )
