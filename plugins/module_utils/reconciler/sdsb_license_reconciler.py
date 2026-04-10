import re

try:
    from ..provisioner.sdsb_license_provisioner import SDSBLicenseProvisioner
    from ..provisioner.sdsb_cluster_provisioner import SDSBClusterProvisioner
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..message.sdsb_license_msgs import SDSBLicenseMsg
except ImportError:
    from provisioner.sdsb_license_provisioner import SDSBLicenseProvisioner
    from provisioner.sdsb_cluster_provisioner import SDSBClusterProvisioner
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from message.sdsb_license_msgs import SDSBLicenseMsg

logger = Log()
AWS = "Amazon.com, Inc"


class SDSBLicenseReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBLicenseProvisioner(self.connection_info)
        self.cluster_prov = SDSBClusterProvisioner(self.connection_info)

    @log_entry_exit
    def get_license_setting_facts(self):
        lic_setting_obj = self.get_license_setting()
        return lic_setting_obj.camel_to_snake_dict()

    @log_entry_exit
    def get_license_setting(self):
        lic_setting_obj = self.provisioner.get_license_setting()
        logger.writeDebug(f"RC:get_license_setting:lic_setting_obj= {lic_setting_obj}")
        return lic_setting_obj

    @log_entry_exit
    def get_license(self, license_id):
        return self.provisioner.get_license_by_id(license_id)

    @log_entry_exit
    def modify_license_setting(self, spec):
        return self.provisioner.modify_license_setting(spec)

    @log_entry_exit
    def get_license_facts(self, spec=None):
        if spec:
            self.validate_license_facts_spec(spec)
        return self.provisioner.get_licenses(spec)

    def validate_license_facts_spec(self, spec):
        valid_status_map = {
            "active": "Active",
            "warning": "Warning",
            "graceperiod": "GracePeriod",
            "invalid": "Invalid",
        }
        if spec.status:
            status_lower = spec.status.lower()
            if status_lower not in valid_status_map:
                raise ValueError(
                    SDSBLicenseMsg.INVALID_STATUS.value.format(
                        spec.status, list(valid_status_map.values())
                    )
                )

            spec.status = valid_status_map[status_lower]

    @log_entry_exit
    def delete_license(self, license_id):
        return self.provisioner.delete_license(license_id)

    @log_entry_exit
    def create_license(self, key_code):
        return self.provisioner.create_license(key_code)

    @log_entry_exit
    def is_modification_needed(self, current_setting, spec):
        change_needed = False
        remaining_days = None
        warning_threshold = spec.warning_threshold_setting
        logger.writeDebug(f"RC:is_modification_needed:spec= {spec}")
        if warning_threshold:
            # Validate remaining_days
            remaining_days = warning_threshold.remaining_days
            if remaining_days is not None:
                if not (-1 <= remaining_days <= 60):
                    raise ValueError(
                        SDSBLicenseMsg.INVALID_REMAINING_DAYS.value.format(
                            remaining_days
                        )
                    )
            else:
                remaining_days = -1

            # Validate total_pool_capacity_rate
            total_pool_capacity_rate = warning_threshold.total_pool_capacity_rate
            if total_pool_capacity_rate is not None:
                if total_pool_capacity_rate != -1 and not (
                    0 <= total_pool_capacity_rate <= 100
                ):
                    raise ValueError(
                        SDSBLicenseMsg.INVALID_TOTAL_POOL_CAPACITY_RATE.value.format(
                            total_pool_capacity_rate
                        )
                    )
            else:
                total_pool_capacity_rate = -1

            if (
                warning_threshold.remaining_days
                != current_setting.warningThresholdSetting.remainingDays
                or warning_threshold.total_pool_capacity_rate
                != current_setting.warningThresholdSetting.totalPoolCapacityRate
            ):
                change_needed = True

        if spec.allow_over_capacity is not None:
            platform = self.cluster_prov.get_platform()
            if platform == AWS:
                if spec.allow_over_capacity != current_setting.overcapacityAllowed:
                    change_needed = True
            else:
                raise ValueError(
                    SDSBLicenseMsg.OVERCAPACITY_NOT_SUPPORTED.value.format(platform)
                )

        return change_needed

    @log_entry_exit
    def reconcile_license_setting(self, spec, state):
        if state == "present":
            # Get current settings
            current_setting = self.get_license_setting()
            logger.writeDebug(f"RC:current_license_setting= {current_setting}")
            needs_update = self.is_modification_needed(current_setting, spec)
            if needs_update:
                license_setting = self.modify_license_setting(spec)
                self.connection_info.changed = True
            else:
                license_setting = current_setting
            logger.writeDebug(f"RC:final_license_setting= {license_setting}")
            return license_setting.camel_to_snake_dict()

    @log_entry_exit
    def validate_create_license_spec(self, spec):
        if not spec.key_code:
            raise ValueError(SDSBLicenseMsg.KEY_CODE_REQD_FOR_CREATE.value)

        # Check length
        if not (1 <= len(spec.key_code) <= 75):
            raise ValueError(
                SDSBLicenseMsg.INVALID_KEY_CODE.value.format(len(spec.key_code))
            )

        # Check if it contains only uppercase alphanumeric characters
        if not re.match(r"^[A-Z0-9]+$", spec.key_code):
            raise ValueError(SDSBLicenseMsg.INVALID_CHARS_IN_KEY_CODE.value)

    @log_entry_exit
    def validate_delete_license_spec(self, spec):
        if not spec.id:
            raise ValueError(SDSBLicenseMsg.ID_REQD_FOR_DELETE.value)

    @log_entry_exit
    def reconcile_license(self, spec, state):
        if state == "present":
            self.validate_create_license_spec(spec)
            # Create a new license
            logger.writeInfo("Creating license with key code")
            create_result = self.create_license(spec.key_code)
            logger.writeDebug(
                f"MOD:hv_sds_block_license:create_result= {create_result}"
            )
            self.connection_info.changed = True
            spec.comments = SDSBLicenseMsg.LICENSE_CREATE_SUCCESS.value
            return create_result
        elif state == "absent":
            self.validate_delete_license_spec(spec)
            existing_license = None
            try:
                # Verify license exists before attempting to delete
                existing_license = self.get_license(spec.id)
            except Exception as e:
                logger.writeException(e)
                spec.comments = str(e)
                return None
            if existing_license is None:
                logger.writeInfo(f"License {spec.id} not found")
                msg = SDSBLicenseMsg.LICENSE_NOT_FOUND.value
            else:
                try:
                    # Delete the license
                    logger.writeInfo(f"Deleting license: {spec.id}")
                    delete_result = self.delete_license(spec.id)
                    logger.writeDebug(
                        f"MOD:hv_sds_block_license:delete_result= {delete_result}"
                    )
                    self.connection_info.changed = True
                    spec.comments = SDSBLicenseMsg.LICENSE_DELETE_SUCCESS.value
                except Exception as e:
                    logger.writeException(e)
                    spec.comments = str(e)
            return None
        else:
            raise ValueError(SDSBLicenseMsg.INVALID_STATE.value.format(state))
