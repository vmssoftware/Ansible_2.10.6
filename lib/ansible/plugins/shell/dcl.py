# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import time
import math
from ansible.module_utils.six import text_type
from ansible.module_utils.six.moves import shlex_quote
from ansible.plugins.shell.sh import ShellModule as ShModule
from ansible.utils.display import Display


DOCUMENTATION = '''
    name: dcl
    version_added: ""
    short_description: shell DCL OpenVMS Command line
    description:
      - This shell plugin is the one you want to use on OpenVMS systems,
    extends_documentation_fragment:
      - shell_common
'''


class ShellModule(ShModule):

    # Common shell filenames that this plugin handles
    COMPATIBLE_SHELLS = frozenset(('dcl',))
    # Family of shells this has.  Must match the filename without extension
    SHELL_FAMILY = 'dcl'
    # commonly used
    ECHO = 'WRITE SYS$OUTPUT "%s"'
    COMMAND_SEP = ' ; '

    _SHELL_EMBEDDED_PY_EOL = '\n'
    _SHELL_REDIRECT_ALLNULL = 'sts = $STATUS ; DEFINE/USER SYS$OUTPUT NL: ; DEFINE/USER SYS$ERROR NL: ; $STATUS = sts'
    _SHELL_AND = ' && '
    _SHELL_OR = ''
    _SHELL_SUB_LEFT = ''
    _SHELL_SUB_RIGHT = ''
    _SHELL_GROUP_LEFT = ''
    _SHELL_GROUP_RIGHT = ''

    def __init__(self):
        super(ShellModule, self).__init__()
        self.ECHO = 'WRITE SYS$OUTPUT "%s"'
        self._IS_OPENVMS = True
        # three bits of $status
        # 0 Warning
        # 1 Success
        # 2 Error
        # 3 Information
        # 4 Fatal (severe) error
        self.vms_status = 0

    def env_prefix(self, **kwargs):
        env = self.env.copy()
        env.update(kwargs)
        return ' '.join(['%s :== "%s"' % (k, text_type(v)) for k, v in env.items()])

    def unix2vms_mode(self, mode):
        prot = ['S:RWED']

        if '+' in mode:
            (who, flag) = mode.split('+')
            if 'u' in who:
                if flag == 'x':
                    prot.append('O:RWED')
                else:
                    prot.append('O:RWD')
            elif 'a' in who:
                if flag == 'x':
                    prot.append('W:RWED')
                else:
                    prot.append('W:RWD')
            else:
                prot.append('O:RWD')
        else:
            prot.append('O:RWD')

        return '(' + ','.join(prot) + ')'

    def unix2vms_path(self, path):
        items = path.split('/')
        path_vms = ''
        shift = 0

        if items[len(items)-1] == '':
            shift = 1

        for j in range(len(items)-shift):
            if path_vms == '':
                path_vms += '[.' + items[j] + '.'
            else:
                if j == len(items)-(shift+1):
                    path_vms += items[j] + ']'
                else:
                    path_vms += items[j] + '.'

        path_vms = path_vms.replace('..', '.^.')
        return path_vms

    def unix2vms_paths(self, paths):
        paths_vms = []
        for i in range(len(paths)):
            items = paths[i].split('/')
            path_vms = ''
            shift = 1

            if items[len(items)-1] == '':
                shift = 2

            for j in range(len(items)-shift):
                if path_vms == '':
                    path_vms += '[.' + items[j] + '.'
                else:
                    if j == len(items)-(shift+1):
                        path_vms += items[j] + ']'
                    else:
                        path_vms += items[j] + '.'

            if shift == 2:
                path_vms += items[len(items)-shift] + '.dir'
            else:
                path_vms += items[len(items)-shift]

            path_vms = path_vms.replace('..', '.^.')
            paths_vms.extend([path_vms])

        return paths_vms

    def chmod(self, paths, mode):
        paths = self.unix2vms_paths(paths)
        cmd = ['']

        for path in paths:
            if len(cmd) == 1:
                cmd.extend(['set security/protection=' + self.unix2vms_mode(mode) + ' ' + path])
            else:
                cmd.extend([';', 'set security/protection=' + self.unix2vms_mode(mode) + ' ' + path])

        return ' '.join(cmd)

    def chown(self, paths, user):
        paths = self.unix2vms_paths(paths)
        cmd = ['set proc/priv=GRPPRV']

        for path in paths:
            cmd.extend([';', 'set security/owner=' + user + ' ' + path])

        return ' '.join(cmd)

    def remove(self, path, recurse=False):
        path = shlex_quote(path)
        cmd = 'delete/tree '
        
        tmpdirt = path.replace('.', '^.')
        items = tmpdirt.split('/')
        path_vms = ''

        for i in range(len(items)-2):
            if items[i] != '':
                if path_vms == '':
                    path_vms += '[.' + items[i] + '.'
                else:
                    if i == len(items)-3:
                        path_vms += items[i] + '...]*.*;*'
                    else:
                        path_vms += items[i] + '.'

        return cmd + "%s ; %s" % (path_vms, 'purge')

    def exists(self, path):
        cmd = ['IF f$search("{0}") .eqs. "" THEN exit 2'.format(path)]
        return ' '.join(cmd)

    @staticmethod
    def _generate_temp_dir_name():
        return 'ans-tmp-%s' % (math.floor(time.time()))

    def mkdtemp(self, basefile=None, system=False, mode=0o700, tmpdir=None):
        if not basefile:
            basefile = self.__class__._generate_temp_dir_name()

        tmpdirt = tmpdir.replace('.', '^.')
        relative_path = tmpdir.split('/', 2)[2] + '/' + basefile
        items = tmpdirt.split('/')
        path_search = ''
        path_folder = ''

        for i in range(len(items)):
            if path_search == '':
                path_search += items[i] + ':['
            else:
                if i == len(items)-1:
                    path_search += items[i]
                else:
                    path_search += items[i] + '.'

        path_folder = path_search + '.' + basefile + ']'
        path_search += ']' + basefile

        return 'IF f$search("{0}.DIR") .eqs. "" THEN CREATE/DIR {1} && WRITE SYS$OUTPUT "{2}"'.format(path_search, path_folder, relative_path)

    def expand_user(self, user_home_path, username=''):
        """ Return a command to expand tildes in a path """
        return 'WRITE SYS$OUTPUT F$TRNLNM("SYS$LOGIN")'

    def pwd(self):
        """ Return the working directory after connecting """
        return 'SHOW DEFAULT'

    def pipe_extend_command(self, cmd):
        """extend command for status"""
        return 'PIPE ({0}) ; SH SYM $status'.format(cmd)

    def quote(self, cmd):
        """ No quoting """
        return cmd