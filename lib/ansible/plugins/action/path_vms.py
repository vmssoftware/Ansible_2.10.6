from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.module_utils.basic import unix_path_to_vms


class ActionModule(ActionBase):
    TRANSFERS_FILES = False

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        unix_path = self._task.args.get('path')
        unix_file_type = self._task.args.get('file_type')
        use_ellipsis = boolean(self._task.args.get('use_ellipsis', False), strict=False)

        if unix_path:
            if unix_file_type:
                unix_file_type = str(unix_file_type)
                if unix_file_type != 'file' and unix_file_type != 'directory':
                    result['failed'] = True
                    result['msg'] = 'option "file_type" is not correct'
                    return result
            else:
                unix_file_type = 'file'

            path = str(unix_path)

            if path.count('/') > 0:
                if path.startswith('/'): # absolute path
                    result['changed'] = True
                    result['path'] = unix_path_to_vms(unix_path, unix_file_type, use_ellipsis)
                else:
                    # relative path
                    result['failed'] = True
                    result['msg'] = 'option "path" is not absolute path'
            else:
                result['failed'] = True
                result['msg'] = 'option "path" is not correct'
        else:
            result['failed'] = True
            result['msg'] = 'option "path" not found'

        return result