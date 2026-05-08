# provisioner/vsp_one_gad_provisioner.py

import re

try:
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_log import Log
    from ..common.vsp_errors import VspFeatureNotSupportedError
    from ..gateway.vsp_one_gad_gateway import VspOneGadGateway
    from ..message.vsp_storage_system_msgs import VspStorageSystemMsg
except ImportError:
    from common.ansible_common import log_entry_exit
    from common.hv_log import Log
    from common.vsp_errors import VspFeatureNotSupportedError
    from gateway.vsp_one_gad_gateway import VspOneGadGateway
    from ..message.vsp_storage_system_msgs import VspStorageSystemMsg

logger = Log()


class VspOneGadProvisioner:
    def __init__(self, connection_info):
        self.gateway = VspOneGadGateway(connection_info)
        self.connection_info = connection_info

        if not self.gateway.is_block_high_end:
            raise VspFeatureNotSupportedError(VspStorageSystemMsg.ONLY_SUPPORTED_ON_BHE.value)

    @log_entry_exit
    def get_gad_pairs_facts(self, spec=None):
        """Returns all GAD pairs as a list of snake_case dictionaries."""
        if spec and spec.primary_volume_id and spec.count == 1:
            return self.get_gad_pair_by_id(spec.primary_volume_id, spec.mirror_unit_number, spec)
        return self.gateway.get_gad_pairs_facts(spec).data_to_snake_case_list()

    @log_entry_exit
    def get_gad_pair_by_id(self, local_volume_id, mu_number, spec):
        """
        Fetches a model from the gateway and converts it to a snake_case dict.
        """
        try:
            response_model = self.gateway.get_gad_pair_by_id(local_volume_id, mu_number)
            if response_model:
                return response_model.camel_to_snake_dict()
            return None
        except Exception as e:
            spec.comments = str(e)
            return None

    @log_entry_exit
    def filter_gad_pairs_by_ids(self, id_list, spec=None):
        """
        Orchestrates the fetch based on list size.
        Returns a list of snake_case dictionaries.
        """
        THRESHOLD = 20
        filtered_gad_pairs = []

        if not id_list:
            return filtered_gad_pairs

        if len(id_list) <= THRESHOLD:
            logger.writeDebug(f"Surgical fetch for {len(id_list)} IDs.")
            for item in id_list:
                try:
                    pvol, mu = item.split(",")
                    # Calling Gateway directly to avoid spec.comments pollution
                    response_model = self.gateway.get_gad_pair_by_id(pvol.strip(), mu.strip())

                    if response_model:
                        # Convert the model to the snake_case dict the Provisioner expects
                        filtered_gad_pairs.append(response_model.camel_to_snake_dict())

                except Exception as e:
                    # Log the error but don't stop the loop;
                    # Missing pairs are handled by the caller via missing_ids logic
                    logger.writeDebug(f"Surgical fetch skipped for {item}: {str(e)}")
        else:
            logger.writeDebug(f"Global fetch for {len(id_list)} IDs.")
            # Use self to keep it consistent with the Provisioner's facts gathering
            all_pairs = self.get_gad_pairs_facts(spec)

            targets = {tuple(id_str.split(",")) for id_str in id_list}

            for gad_pair in all_pairs:
                current = (
                    str(gad_pair.get("primary_volume_id", "")),
                    str(gad_pair.get("mirror_unit_number", "")),
                )
                if current in targets:
                    filtered_gad_pairs.append(gad_pair)

        return filtered_gad_pairs

    @log_entry_exit
    def delete_gad_pairs(self, spec):
        """
        Deletes GAD pairs via the Gateway.
        Validates existence, splits PAIRs, waits for PSUS, then deletes.
        """
        import time
        from copy import deepcopy

        try:
            # 1. Identify target IDs from user input
            original_mirrors = spec.primary_volume_mirrors
            target_ids = [f"{m.get('primary_volume_id')},{m.get('mirror_unit_number')}" for m in original_mirrors]
            logger.writeDebug(f"Provisioner:delete_gad_pairs: Target IDs: {target_ids}")

            # 2. Status Fetch with 404 Protection
            current_pairs = []
            try:
                # We fetch current status to see what actually exists on the storage
                current_pairs = self.filter_gad_pairs_by_ids(target_ids, spec)
            except Exception as fetch_error:
                logger.writeDebug(f"Provisioner:delete_gad_pairs: Fetch failed (likely 404): {str(fetch_error)}")
                current_pairs = []

            # Map existing pairs for lookup
            existing_ids = {f"{p.get('primary_volume_id')},{p.get('mirror_unit_number')}" for p in current_pairs}
            missing_ids = [tid for tid in target_ids if tid not in existing_ids]

            # 3. Handle existence logic (Unified for 1 or many)
            if missing_ids:
                if not existing_ids:
                    # Case: NOTHING exists. Return success immediately (Idempotent)
                    spec.comments = f"GAD pair(s) {missing_ids} not found. No deletion required."
                    return True

                # Case: SOME exist. Filter the spec so API calls only include valid resources.
                logger.writeWarning(f"Provisioner:delete_gad_pairs: Filtering out missing pairs: {missing_ids}")

                # Update the mirror list (objects)
                spec.primary_volume_mirrors = [m for m in original_mirrors if f"{m.get('primary_volume_id')},{m.get('mirror_unit_number')}" in existing_ids]

                # Update the flat ID list (strings) to prevent Gateway from using stale data
                if hasattr(spec, "ids"):
                    spec.ids = [tid for tid in target_ids if tid in existing_ids]

            # 4. Filter ONLY EXISTING pairs that need splitting
            # This prevents sending missing IDs to the suspend API (fixes 400 Error)
            pairs_to_split = []
            for p in current_pairs:
                pvol_id = p.get("primary_volume_id")
                mu_number = p.get("mirror_unit_number")
                pair_id = f"{pvol_id},{mu_number}"

                if p.get("primary_volume_status") == "PAIR" and pair_id in existing_ids:
                    pairs_to_split.append({"primary_volume_id": pvol_id, "mirror_unit_number": mu_number})

            # 5. Execute Split and Wait
            if pairs_to_split:
                logger.writeInfo(f"Provisioner:delete_gad_pairs: Suspending {len(pairs_to_split)} synchronized pairs.")

                suspend_spec = deepcopy(spec)
                # CHANGE 1: Ensure the spec for the API call ONLY has the split-able pairs
                suspend_spec.primary_volume_mirrors = pairs_to_split

                if not getattr(suspend_spec, "continue_io_volume", None):
                    suspend_spec.continue_io_volume = "PRIMARY"

                logger.writeDebug(f"Provisioner:delete_gad_pairs: Suspend spec: {suspend_spec}.")
                if not self.gateway.suspend_gad_pairs(suspend_spec):
                    spec.comments = "Delete failed: Pre-delete split call failed."
                    return False

                # --- Wait Logic ---
                logger.writeDebug("Provisioner:delete_gad_pairs: Waiting for PSUS transition...")
                max_retries = 10
                retry_interval = 2  # seconds

                # CHANGE 2: Only poll for IDs that actually exist to avoid 404s in the loop
                valid_poll_ids = [f"{p['primary_volume_id']},{p['mirror_unit_number']}" for p in pairs_to_split]

                for attempt in range(max_retries):
                    time.sleep(retry_interval)
                    # Use valid_poll_ids instead of target_ids
                    check_pairs = self.filter_gad_pairs_by_ids(valid_poll_ids, spec)

                    pending = [cp.get("primary_volume_id") for cp in check_pairs if cp.get("primary_volume_status") == "PAIR"]

                    if not pending:
                        logger.writeDebug(f"Provisioner:delete_gad_pairs: Split successful after {attempt + 1} checks.")
                        break
                    logger.writeDebug(f"Provisioner:delete_gad_pairs: Still waiting for {pending} (Attempt {attempt + 1}).")
                else:
                    logger.writeWarning("Provisioner:delete_gad_pairs: Timeout waiting for split. Proceeding anyway.")

            # 6. Final Deletion (Only includes verified existing IDs)
            response = self.gateway.delete_gad_pairs(spec)

            if response:
                self.connection_info.changed = True
                msg = f"GAD pair(s) {response} deleted successfully"
                if missing_ids:
                    msg += f". Note: {missing_ids} not found/skipped"
                spec.comments = msg
                return True

            return False

        except Exception as e:
            logger.writeError(f"Provisioner:delete_gad_pairs: Exception: {str(e)}")
            spec.comments = f"Delete failed: {self._get_clean_error_message(str(e))}"
            return False

    @log_entry_exit
    def suspend_gad_pairs(self, spec):
        """
        Suspends Host I/O and splits the GAD pair.
        Fails if any pair is missing. Skips already suspended (PSUS/SSUS). Includes PSUE.
        """
        try:
            # 1. Identify target IDs from user input
            original_mirrors = spec.primary_volume_mirrors
            target_ids = [f"{m.get('primary_volume_id')},{m.get('mirror_unit_number')}" for m in original_mirrors]

            # 2. Status Fetch with 404 Protection
            current_pairs = []
            try:
                current_pairs = self.filter_gad_pairs_by_ids(target_ids, spec)
            except Exception as fetch_error:
                logger.writeDebug(f"Provisioner:suspend_gad_pairs: Fetch failed: {str(fetch_error)}")
                current_pairs = []

            # Map existing pairs for lookup
            existing_ids = {f"{p.get('primary_volume_id')},{p.get('mirror_unit_number')}" for p in current_pairs}
            missing_ids = [tid for tid in target_ids if tid not in existing_ids]

            # 3. Strict Existence Check
            if missing_ids:
                spec.comments = f"Suspend failed: GAD pair(s) {missing_ids} not found on the storage system."
                logger.writeError(f"Provisioner:suspend_gad_pairs: {spec.comments}")
                return False

            # 4. Identify pairs that need a suspend call
            suspended_statuses = ["PSUS", "SSUS"]

            ids_needing_suspend = [
                f"{p.get('primary_volume_id')},{p.get('mirror_unit_number')}" for p in current_pairs if p.get("primary_volume_status") not in suspended_statuses
            ]

            already_suspended_ids = [
                f"{p.get('primary_volume_id')},{p.get('mirror_unit_number')}" for p in current_pairs if p.get("primary_volume_status") in suspended_statuses
            ]

            # 5. Handle Skip Logic
            if already_suspended_ids:
                if not ids_needing_suspend:
                    spec.comments = f"No suspension required. GAD pair(s) {already_suspended_ids} are already suspended."
                    return True

                logger.writeInfo(f"Provisioner:suspend_gad_pairs: Skipping already suspended: {already_suspended_ids}")

                spec.primary_volume_mirrors = [
                    m for m in original_mirrors if f"{m.get('primary_volume_id')},{m.get('mirror_unit_number')}" in ids_needing_suspend
                ]

                if hasattr(spec, "ids"):
                    spec.ids = ids_needing_suspend

            # 6. Execute Suspend
            response = self.gateway.suspend_gad_pairs(spec)
            if response:
                self.connection_info.changed = True
                msg = f"GAD pairs suspended successfully: {response}"
                if already_suspended_ids:
                    msg += f". Note: Skipped {already_suspended_ids} (already suspended)"
                spec.comments = msg
                return True

            return False

        except Exception as e:
            logger.writeError(f"Provisioner:suspend_gad_pairs: Error: {str(e)}")
            spec.comments = f"Suspend failed: {self._get_clean_error_message(str(e))}"
            return False

    @log_entry_exit
    def resync_gad_pairs(self, spec):
        """
        Resynchronizes the GAD pair.
        Fails if any pair is missing. Skips pairs already in PAIR status.
        """
        try:
            # 1. Identify target IDs from user input
            original_mirrors = spec.primary_volume_mirrors
            target_ids = [f"{m.get('primary_volume_id')},{m.get('mirror_unit_number')}" for m in original_mirrors]

            # 2. Status Fetch with 404 Protection
            current_pairs = []
            try:
                current_pairs = self.filter_gad_pairs_by_ids(target_ids, spec)
            except Exception as fetch_error:
                logger.writeDebug(f"Provisioner:resync_gad_pairs: Fetch failed: {str(fetch_error)}")
                current_pairs = []

            # Map existing pairs for lookup
            existing_ids = {f"{p.get('primary_volume_id')},{p.get('mirror_unit_number')}" for p in current_pairs}
            missing_ids = [tid for tid in target_ids if tid not in existing_ids]

            # 3. Strict Existence Check
            if missing_ids:
                spec.comments = f"Resync failed: GAD pair(s) {missing_ids} not found on the storage system."
                logger.writeError(f"Provisioner:resync_gad_pairs: {spec.comments}")
                return False

            # 4. Identify pairs that need resync (Skip healthy PAIRs)
            ids_needing_resync = [
                f"{p.get('primary_volume_id')},{p.get('mirror_unit_number')}" for p in current_pairs if p.get("primary_volume_status") != "PAIR"
            ]

            already_synced_ids = [
                f"{p.get('primary_volume_id')},{p.get('mirror_unit_number')}" for p in current_pairs if p.get("primary_volume_status") == "PAIR"
            ]

            # 5. Handle Skip Logic
            if already_synced_ids:
                if not ids_needing_resync:
                    spec.comments = f"No resync required. GAD pair(s) {already_synced_ids} are already in PAIR status."
                    return True

                logger.writeInfo(f"Provisioner:resync_gad_pairs: Skipping already synced: {already_synced_ids}")

                spec.primary_volume_mirrors = [
                    m for m in original_mirrors if f"{m.get('primary_volume_id')},{m.get('mirror_unit_number')}" in ids_needing_resync
                ]

                if hasattr(spec, "ids"):
                    spec.ids = ids_needing_resync

            # 6. Execute Resync
            response = self.gateway.resync_gad_pairs(spec)
            if response:
                self.connection_info.changed = True
                msg = f"GAD pairs resynchronized successfully: {response}"
                if already_synced_ids:
                    msg += f". Note: Skipped {already_synced_ids} (already synced)"
                spec.comments = msg
                return True

            return False

        except Exception as e:
            logger.writeError(f"Provisioner:resync_gad_pairs: Error: {str(e)}")
            spec.comments = f"Resync failed: {self._get_clean_error_message(str(e))}"
            return False

    def _get_clean_error_message(self, error_msg):
        """
        Translates backend API parameters and strictly removes line/column
        metadata along with surrounding commas and whitespace.
        """
        if not error_msg or not isinstance(error_msg, str):
            return error_msg

        # 1. Remove 'line=X' and 'column=Y' and any immediately following commas/spaces
        # \b ensures we match the whole word.
        # [,?\s]* matches optional commas or spaces following the number.
        clean_msg = re.sub(r"\b(line|column)=\d+[,?\s]*", "", error_msg)

        # 2. Cleanup punctuation artifacts
        # Remove any colons that are now empty or double commas
        clean_msg = re.sub(r",\s*,", ",", clean_msg)  # Remove double commas
        clean_msg = re.sub(r":\s*([,.\s]*)$", "", clean_msg)  # Remove trailing colons/dots
        clean_msg = re.sub(r":\s*,", ":", clean_msg)  # Fix ": ," to ":"

        # 3. Mapping: "Backend API Path": "Spec Field Name"
        translation_map = {
            "param.ids.muNumber": "mirror_unit_number",
            "param.ids.localVolumeId": "primary_volume_id",
            "param.ids": "primary_volume_mirrors",
            "continueIoVolume": "continue_io_volume",
            "copyPace": "copy_pace",
            "ioPreference": "io_preference",
            "isSwapResynced": "is_swap_resynced",
            "deleteMode": "delete_mode",
        }

        for api_field, spec_field in translation_map.items():
            clean_msg = clean_msg.replace(api_field, f"'{spec_field}'")

        return clean_msg.strip()
