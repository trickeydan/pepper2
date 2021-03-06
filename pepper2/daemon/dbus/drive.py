"""Classes to interact with drives."""

from pathlib import Path
from typing import Any, Type

from pkg_resources import resource_string

from pepper2.common.drive_types import DRIVE_TYPES, DriveType
from pepper2.daemon.publishable_group import PublishableGroup

DriveGroup = PublishableGroup['Drive']


class Drive:
    """An individual drive."""

    dbus = resource_string(__name__, "drive.xml").decode('utf-8')

    def __init__(
            self,
            *,
            uuid: str,
            mount_path: Path,
            drive_type: Type[DriveType],
    ):
        self._uuid = uuid
        self._mount_path = mount_path
        self._drive_type = drive_type

    @classmethod
    def from_proxy(cls, proxy_object: Any) -> 'Drive':  # type: ignore
        """
        Construct a proper drive object from a proxy object.

        There are some types that we want to use, but cannot send
        over DBus, for example Path and Type[DriveType]. This is
        thus part of the slightly hacky code that we use to ensure
        a nicely typed API on both sides of the bus.
        """
        return Drive(
            uuid=proxy_object.uuid,
            mount_path=Path(proxy_object.mount_path_str),
            drive_type=DRIVE_TYPES[proxy_object.drive_type_index],
        )

    @property
    def uuid(self) -> str:
        """The UUID of the drive."""
        return self._uuid

    @property
    def mount_path(self) -> Path:
        """The mount path of the drive."""
        return self._mount_path

    @property
    def drive_type(self) -> Type[DriveType]:
        """The DriveType class of this drive."""
        return self._drive_type

    @drive_type.setter
    def drive_type(self, drive_type: Type[DriveType]) -> None:
        """
        The DriveType class of this drive.

        A drivetype should only be changed if it is dangerous
        to use the drive otherwise.
        """
        self._drive_type = drive_type

    @property
    def drive_type_index(self) -> int:
        """
        An integer representation of the drive type.

        For transmission over DBus.
        """
        return DRIVE_TYPES.index(self.drive_type)

    @property
    def mount_path_str(self) -> str:
        """
        A string representation of the mount path.

        For transmission over DBus.
        """
        return str(self.mount_path.absolute())
