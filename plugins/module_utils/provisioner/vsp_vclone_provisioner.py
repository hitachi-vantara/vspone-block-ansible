try:
    from ..gateway.vsp_vclone_gateway import VSPVcloneGateway
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit

except ImportError:
    from gateway.vsp_vclone_gateway import VSPVcloneGateway
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class VSPVcloneProvisioner:

    def __init__(self, connection_info, serial=None):
        self.gateway = VSPVcloneGateway(connection_info)
        self.connection_info = connection_info
        self.serial = serial
        if serial:
            self.gateway.set_serial(serial)

    @log_entry_exit
    def get_vclone_parent_volumes(self):
        """Get Vclone Parent Volumes"""

        vclone_parent_volumes = self.gateway.get_vclone_parent_volumes()

        logger.writeDebug(
            f"PROV:get_vclone_parent_volumes:vclone_parent_volumes: {vclone_parent_volumes}"
        )
        return vclone_parent_volumes

    @log_entry_exit
    def is_vclone_supported(self):
        return self.gateway.is_vclone_supported()
