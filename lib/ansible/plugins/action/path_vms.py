from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    TRANSFERS_FILES = False

    def unix_path_to_vms(self, path, type):
        symbols = ['^', ',', ';', '[', ']', '%', '&']

        for symbol in symbols:
            path = path.replace(symbol, '^' + symbol)

        items = path.split('/')
        path_vms = ''
        file_name = ''
        shift = 1

        if type != 'directory':
            shift = 2

        for i in range(len(items)-shift+1):
            if items[i] != '':
                items[i] = items[i].replace('.', '^.')
                if path_vms == '':
                    path_vms += items[i] + ':['
                else:
                    if i == len(items)-shift:
                        path_vms += items[i] + ']'
                    else:
                        path_vms += items[i] + '.'

        if type != 'directory':
            count_dot = items[len(items)-1].count('.')
            file_name = items[len(items)-1].replace('.', '^.', count_dot-1)

        return path_vms + file_name

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        unix_path = self._task.args.get('path')
        unix_file_type = self._task.args.get('file_type')

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
                    result['path'] = self.unix_path_to_vms(unix_path, unix_file_type)
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