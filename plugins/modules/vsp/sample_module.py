from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: sample_module
short_description: This is a sample module
description:
    - This module takes a name as input and returns a greeting message.
options:
    name:
        description:
            - The name to be greeted.
        required: true
        type: str
author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = '''
# Pass in a name
- name: Test with a name
    sample_module:
        name: John

# Pass in another name
- name: Test with another name
    sample_module:
        name: Jane

# For more information, visit the documentation at:
# https://docs.ansible.com/ansible/latest/modules/sample_module.html
# Sample [here] (docs/vsp/sample_playbook.yml)
'''

# For more information, visit the documentation at:
# https://docs.ansible.com/ansible/latest/modules/sample_module.html

#!/usr/bin/python


def run_module():
    module_args = dict(
        name=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    result['original_message'] = module.params['name']
    result['message'] = 'Hello, {}'.format(module.params['name'])
    result['changed'] = True

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()