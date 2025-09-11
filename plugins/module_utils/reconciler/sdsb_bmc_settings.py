try:
    from ..provisioner.sdsb_bmc_settings_provisioner import SDSBBmcSettingsProvisioner
    from ..provisioner.sdsb_cluster_provisioner import SDSBClusterProvisioner
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..message.sdsb_bmc_connection_msgs import SDSBBmcConnectionValidationMsg
except ImportError:
    from provisioner.sdsb_bmc_settings_provisioner import SDSBBmcSettingsProvisioner
    from provisioner.sdsb_cluster_provisioner import SDSBClusterProvisioner
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from message.sdsb_bmc_connection_msgs import SDSBBmcConnectionValidationMsg

logger = Log()


class SDSBBmcSettingsReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBBmcSettingsProvisioner(self.connection_info)
        self.cluster_prov = SDSBClusterProvisioner(self.connection_info)

    @log_entry_exit
    def get_storage_node_bmc_settings(self, spec=None):
        cloud_platforms = ["Google, Inc.", "Msft", "Amazon.com, Inc"]
        platform = self.cluster_prov.get_platform()
        logger.writeDebug(f"add_storage_node:spec = {spec}  platform = {platform}")
        if platform in cloud_platforms:
            raise ValueError(
                SDSBBmcConnectionValidationMsg.NOT_SUPPORTED_ON_CLOUD.value
            )
        if spec is None:
            return self.provisioner.get_bmc_settings_for_all_storage_nodes()
        else:
            return self.provisioner.get_bmc_settings_for_one_storage_node(spec.id)
