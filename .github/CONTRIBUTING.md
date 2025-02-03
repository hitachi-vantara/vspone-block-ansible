# Contributing

## Bugs, Questions or Feature requests
Please create a new [issue](https://github.com/hitachi-vantara/vspone-block-ansible/issues). When creating an issue the following information should be added to the issue to help the team(s) make practical progress.

- Version of Hitachi storage Ansible modules 
- Operating system
- Which integration approach is in use: Direct access or API Gateway
- Storage system type(s) under management
- Python version in use

For a howto on creating a GitHub issue please review [Creating an issue from a repository](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue#creating-an-issue-from-a-repository) from the GitHub documentation.

## Improvements

If there is an example playbook, new Python module, or documentation change you'd like to contribute we recommend that you [fork the repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo), make your change(s), and then create a [Pull Request](https://github.com/marketplace/actions/create-pull-request). From there we will evaluate the request and handle it appropriately.

## Troubleshooting
To help in diagnosing problems the following can help you to gather logs.

- Set these environment variables to change the Ansible logging level, logging directory and log file name
  - `HV_ANSIBLE_LOG_PATH` - defaults to `$HOME/logs/hitachivantara/ansible/vspone_block/`
  - `HV_ANSIBLE_LOG_LEVEL` - defaults to <NEED HELP HERE TO UNDERSTAND THE DEFAULT LOGGING BEHAVIOR>
  - `HV_ANSIBLE_LOG_FILE` - defaults to `hv_vspone_block_modules.log`

- Hitachi Ansible Storage Log Collection playbooks located in the Ansible installation directory, typically `$HOME/.ansible/ansible_collections/hitachivantara/vspone_block/tools`. The name of the playbooks are:
  - `logbundle_direct_connection.yml` - used when directly communicating to the storage systems
  - `logbundle_gateway_connection.yml` - used when communicating to the storage systems through the gateway
  
- Running the logs collection playbooks
  - <EXAMPLE OF DIRECT RUN>
  - <EXAMPLE OF GATEWAY RUN>

- Log output is stored as a ZIP archive is generally named`ansible_log_bundle_<DATE_TIMESTAMP>.zip` and created in `$HOME/logs/hitachivantara/ansible/vspone_block/log_bundles/`.
    

## Changelog
Review the [changelog](docs/Changelog.md) to track improvements over time.