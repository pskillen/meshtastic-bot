from abc import ABC
import datetime

from src.data_classes import MeshNode


class AbstractModelSerializer(ABC):
    @classmethod
    def to_api_dict(cls, model) -> dict:
        raise NotImplementedError

    @classmethod
    def from_api_dict(cls, model_data: dict):
        raise NotImplementedError

    @staticmethod
    def date_to_api(date: datetime.datetime) -> str:
        return date.strftime("%Y-%m-%d %H:%M:%SZ")

    @staticmethod
    def date_from_api(date_str: str) -> datetime.datetime:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%SZ")


class PositionSerializer(AbstractModelSerializer):
    @classmethod
    def to_api_dict(cls, position: MeshNode.Position) -> dict:
        return {
            "logged_time": cls.date_to_api(position.logged_time),
            "reported_time": cls.date_to_api(position.reported_time),
            "latitude": position.latitude,
            "longitude": position.longitude,
            "altitude": position.altitude,
            "location_source": position.location_source,
        }

    @classmethod
    def from_api_dict(cls, position_data: dict) -> MeshNode.Position:
        return MeshNode.Position(
            logged_time=cls.date_from_api(position_data['logged_time']),
            reported_time=cls.date_from_api(position_data['reported_time']),
            latitude=position_data['latitude'],
            longitude=position_data['longitude'],
            altitude=position_data['altitude'],
            location_source=position_data['location_source']
        )


class DeviceMetricsSerializer(AbstractModelSerializer):
    @classmethod
    def to_api_dict(cls, device_metrics: MeshNode.DeviceMetrics) -> dict:
        return {
            "logged_time": cls.date_to_api(device_metrics.logged_time),
            "battery_level": device_metrics.battery_level,
            "voltage": device_metrics.voltage,
            "channel_utilization": device_metrics.channel_utilization,
            "air_util_tx": device_metrics.air_util_tx,
            "uptime_seconds": device_metrics.uptime_seconds
        }

    @classmethod
    def from_api_dict(cls, device_metrics_data: dict) -> MeshNode.DeviceMetrics:
        return MeshNode.DeviceMetrics(
            logged_time=cls.date_from_api(device_metrics_data['logged_time']),
            battery_level=device_metrics_data['battery_level'],
            voltage=device_metrics_data['voltage'],
            channel_utilization=device_metrics_data['channel_utilization'],
            air_util_tx=device_metrics_data['air_util_tx'],
            uptime_seconds=device_metrics_data['uptime_seconds']
        )


class MeshNodeSerializer(AbstractModelSerializer):
    # BE CAREFUL: The API node/user models do not match the local node/user models (same fields, moved around)

    @classmethod
    def to_api_dict(cls, node: MeshNode) -> dict:
        node_data = {
            "id": node.user.id,
            "macaddr": node.user.macaddr,
            "hw_model": node.user.hw_model,
            "public_key": node.user.public_key,
            'user': {
                "long_name": node.user.long_name,
                "short_name": node.user.short_name
            }
        }

        if node.position:
            node_data['position'] = PositionSerializer.to_api_dict(node.position)

        if node.device_metrics:
            node_data['device_metrics'] = DeviceMetricsSerializer.to_api_dict(node.device_metrics)

        return node_data

    @classmethod
    def from_api_dict(cls, node_data: dict) -> MeshNode:
        user_data = node_data['user']
        user = MeshNode.User(
            node_id=node_data['id'],
            macaddr=node_data['macaddr'],
            hw_model=node_data['hw_model'],
            public_key=node_data['public_key'],
            long_name=user_data['long_name'],
            short_name=user_data['short_name']
        )

        position_data = node_data.get('position')
        position = None
        if position_data:
            position = PositionSerializer.from_api_dict(position_data)

        device_metrics_data = node_data.get('device_metrics')
        device_metrics = None
        if device_metrics_data:
            device_metrics = DeviceMetricsSerializer.from_api_dict(device_metrics_data)

        node = MeshNode()
        node.user = user
        node.position = position
        node.device_metrics = device_metrics

        return node
