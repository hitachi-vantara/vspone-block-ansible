try:
    from ..gateway.vsp_snapshot_family_gateway import VSPSnapshotFamilyGateway
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit

except ImportError:
    from gateway.vsp_snapshot_family_gateway import VSPSnapshotFamilyGateway
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class VSPSnapshotFamilyProvisioner:

    def __init__(self, connection_info, serial=None):
        self.gateway = VSPSnapshotFamilyGateway(connection_info)
        self.connection_info = connection_info
        self.serial = serial
        if serial:
            self.gateway.set_serial(serial)

    @log_entry_exit
    def get_snapshot_family(self, ldev_id):
        """Get Snapshot Family"""

        snapshot_family = self.gateway.get_snapshot_family(ldev_id)

        logger.writeDebug(
            f"PROV:get_snapshot_family:snapshot_family: {snapshot_family}"
        )
        return snapshot_family

    @log_entry_exit
    def is_vclone_supported(self):
        return self.gateway.is_vclone_supported()
