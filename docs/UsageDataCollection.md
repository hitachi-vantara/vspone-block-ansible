# Usage data collection

Hitachi Vantara LLC collects usage data such as storage model, storage serial number,
operation name, status (success or failure), and duration. This data is collected for product
improvement purposes only. It remains confidential and it is not shared with any third parties.

For new installations, usage data collection is enabled by default. A notice is
shown on the first three module executions sharing the same consent file. Each
notice explains that data is being collected and how to opt out. After the third
notice, collection remains enabled unless you opt out.

Existing explicit opt-in or opt-out choices are preserved without further
notices. To opt out, run the following playbook and answer **No**. Answer **Yes**
to opt in explicitly; either choice stops any remaining notices.

Consent-file updates are locked and written atomically so parallel module
executions share the three-notice limit and do not overwrite a choice recorded
by the consent playbook.

If an existing consent record is unreadable or invalid, usage data collection is
disabled and a diagnostic is returned/logged. The record is not reset to default
opt-in. Check file permissions and repair invalid JSON or consent fields before
running the consent playbook to record your choice. An absent consent file is
treated as a new installation; deleting it resets consent and the notice count.

accept_user_consent.yml file path:

```hcl
$HOME/ansible/hitachivantara/vspone_block/playbooks/accept_user_consent.yml
```

After updating user consent, a record is saved at this location:

File path:

```hcl
$HOME/ansible/hitachivantara/vspone_block/user_consent/user_consent.json
```

The accept_user_consent.yml playbook can be executed again to
disable/enable user consent.

Ansible playbook execution results (successes or failures) are automatically logged to Hitachi
Vantara module-specific counters in a usage.json file.

For example, after a get lun facts task execution by a playbook, a
hv_hg_facts.get_luns success counter is incremented.

Sample usage counters are shown below:

```hcl
"hv_hg_facts.get_luns": {
  "success": 1,
  "failure": 0,
  "averageTimeInSec": 0.4
}
```

The averageTimeInSec counter tracks the average call duration in seconds.

The usage.json file is available at: /$HOME/ansible/hitachivantara/
vspone_block/usages/

The failure counter is incremented if the API call fails during Ansible
playbook execution.

In case the usage.json file has been corrupted, during the next round of Ansible playbook
execution, the existing usage.json is moved to the following directory: $HOME/ansible/
hitachivantara/vspone_block/registration/backup/usage.json

All subsequent Ansible playbook execution results will be logged in a new usage.json file
created in the /$HOME/ansible/hitachivantara/vspone_block/usages/ directory.

The usage.json and user_consent.json files are collected when the
Ansible log bundle is generated.

### Requirements for the Ansible client to support Telemetry - Usage data collection

**Unrestricted Outgoing Traffic:**
Ensure that the client's firewall or security software allows outgoing HTTPS traffic on
port 443.

**Proxy Settings:**

- If the client is behind a proxy, verify that the proxy allows the CONNECT method on
port 443 for HTTPS connections.
- Configure proxy settings in the client application if needed.

**Trusted Certificates:**
Ensure the client's certificate store trusts the Certificate Authority (CA) that issued the
server's SSL/TLS certificate. This is crucial for establishing a secure connection.

**TLS/SSL Compatibility:**
Confirm that the client supports the required TLS versions (e.g., TLS 1.2 or 1.3) used
by the server.

**DNS Resolution:**
Make sure the client can resolve the API's domain name correctly to establish a
connection over port 443.

### Sample usage data collected

```hcl
{
  "vspStorages": [
  {
    "directConnectTasks": [
    {
      "hv_hg_facts.get_host_groups": {
        "averageTimeInSec": 0.44,
        "success": 2,
        "failure": 0
      }
    }
  ],
    "serial": 880050,
    "model": "VSP One B28"
  },
  {
    "directConnectTasks": [
      {
        "hv_iscsi_target_facts.get_iscsi_targets": {
        "averageTimeInSec": 3.32,
        "success": 2,
       "failure": 0
      }
    }
    ],
    "serial": 990045,
    "model": "VSP One B26"
  }
  ],
  "site": "3cbb6674-5b7d-43ae-a614-c4b4dafebbea",
  "lastUpdate": "2025-02-19T02:25:08.256861Z",
  "createDate": "2025-02-19T02:22:19.132434Z"
}

```
