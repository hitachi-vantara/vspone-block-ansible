# Hitachi Virtual Storage Platform One Block Storage Modules for Red Hat® Ansible® 4.4.0

The Hitachi Virtual Storage Platform One Block Storage Modules provide a comprehensive set of Ansible modules for managing VSP block storage systems (VSP One Block, VSP 5000 series, VSP E series, VSP F series, and VSP G series) and VSP One SDS Block and Cloud systems. These modules enable seamless integration with Red Hat Ansible, allowing users to automate storage provisioning, configuration, and management tasks.

## Hardware requirements

- VSP One SDS Block and Cloud systems for AWS, Azure, and Google Cloud and VSP One SDS Block for Bare Metal v1.18
- VSP One Block 24
- VSP One Block 26
- VSP One Block 28
- VSP 5100, 5500, 5100H, 5500H, 5200, 5600, 5200H, 5600H (SAS)
- VSP 5100, 5500, 5100H, 5500H, 5200, 5600, 5200H, 5600H (NVMe)
- VSP E590, E790, E990, E1090
- VSP F350, F370, F700, F800, F900, F1000, F1500
- VSP G350, G370, G700, G900, G1000, G1500

## Software requirements

- Red Hat Ansible Core - 2.16, 2.17, 2.18
- Python - 3.9 or higher

## Supported operating systems

- Oracle Enterprise Linux 8.9 or higher
- Red Hat Enterprise Linux 8.9 or higher

## Recommended Host configuration

- CPU/vCPU - 2
- Memory - 4 GB
- HardDisk - 30 GB

## Idempotence

- Idempotence is supported for this release

## Changelog

View the [Changelog](https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/CHANGELOG.rst).

## Available Modules

For a detailed list of available modules, please refer to the [Modules Documentation](https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/docs/MODULES.md).

## Installation

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:

```bash
ansible-galaxy collection install hitachivantara.vspone_block
```

```text
collections:
    - hitachivantara.vspone_block.sds_block
```

```text
collections:
    - hitachivantara.vspone_block.vsp
```

Note that if you install the collection from Ansible Galaxy, it will not be upgraded automatically when you upgrade the Ansible package.

To upgrade the collection to the latest available version, run the following command:

```bash
ansible-galaxy collection install hitachivantara.vspone_block --upgrade
```

If you need to install a specific version of the collection (for example, to downgrade due to issues in the latest version), you can use the following syntax to install version 4.4.0:

```bash
ansible-galaxy collection install hitachivantara.vspone_block:==4.4.0
```

See [using Ansible collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

## Troubleshooting

For troubleshooting tips and common issues, please refer to the [Troubleshooting Guide](https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/docs/TROUBLESHOOTING.md).

## Testing

This collection has been tested using the following methods:

### Sanity Tests

```bash
ansible-test sanity
```

## Use Cases

Below is an example of how this collection can be used to manage a VSP One Block storage system:

### Create an LDEV with a specific LDEV ID

This example shows how to create a logical device (LDEV) with a specific ID, pool, and size.

```yaml
- name: Create LDEV with specific ID
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create ldev
      hitachivantara.vspone_block.vsp.hv_ldev:
        connection_info: "{{ connection_info }}"
        state: "present"
        spec:
          ldev_id: 345
          pool_id: 15
          size: "1GB"
      register: result

    - name: Debug the result variable
      ansible.builtin.debug:
        var: result
```

## Support

As Red Hat Ansible Certified Content, this collection is entitled to support through the Ansible Automation Platform (AAP) using the **Create issue** button on the top right corner.

If a support case cannot be opened with Red Hat and the collection has been obtained either from Galaxy or GitHub, there may be community help available on the [Ansible Forum](https://forum.ansible.com/).

For additional support, please use one of the following channels:

- [GitHub Issues](https://github.com/hitachi-vantara/vspone-block-ansible/issues) – for bug reports, feature requests, and technical assistance
- [Hitachi Vantara Support Portal](https://support.hitachivantara.com/) – for enterprise-grade support (requires valid Hitachi Vantara support contract)

## Release Notes and Roadmap

### Release Notes

Version **4.4.0** highlights:

- General performance enhancements and bug fixes

### Roadmap

- Feature enhancements and new module development
- Ongoing bug fixes and maintenance

## License

[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Author

*This collection was created by the Hitachi Vantara® Ansible Team in 2025.*
