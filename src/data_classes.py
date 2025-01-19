# MeshtasticBot/src/data_classes.py
from typing import Optional


class User:
    id: str
    long_name: str
    short_name: str
    macaddr: str
    hw_model: str
    public_key: str


class Position:
    altitude: int
    time: int
    location_source: str
    latitude: float
    longitude: float


class DeviceMetrics:
    battery_level: int
    voltage: float
    channel_utilization: float
    air_util_tx: float
    uptime_seconds: int


class MeshNode:
    num: int
    user: Optional[User]
    position: Optional[Position]
    last_heard: int
    device_metrics: Optional[DeviceMetrics]
    is_favorite: bool
    packets_today: int
