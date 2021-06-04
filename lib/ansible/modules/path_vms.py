#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, OpenVMS Software Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: path_vms
short_description: Convert UNIX path
description:
- This module converts absolute UNIX paths to OpenVMS.
options:
  path:
    description:
      - Path to the file or directory in UNIX format.
    type: path
    required: yes
  file_type:
    description:
      - Type of path.
    type: str
    choices: [ directory, file ]
    default: file
'''

EXAMPLES = r'''
- name: convert unix path
  path_vms:
    path: "/path/user/folder/file.txt"
    file_type: file
  register: result

- name: verify result
  assert:
    that:
      - result is changed
      - result.path == "path:[user.folder]file.txt"
'''
