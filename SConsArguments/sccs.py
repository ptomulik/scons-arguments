"""`SConsArguments.sccs`

Defines arguments related to SCCS tool

**Arguments**

Programs:
    SCCS
        The SCCS executable

Flags for programs:
    SCCSFLAGS
        General options that are passed to SCCS

    SCCSGETFLAGS
        Options that are passed specifically to the SCCS "get" subcommand
"""

#
# Copyright (c) 2017 by Pawel Tomulik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

__docformat__ = "restructuredText"

from SConsArguments.Util import flags2list
from SConsArguments.Importer import export_arguments

_all_arguments = {
  'SCCS' : {
      'help'        : 'The SCCS executable',
      'metavar'     : 'PROG'
  },
  'SCCSFLAGS' : {
      'help'        : 'General options that are passed to SCCS',
      'metavar'     : 'FLAGS',
      'converter'   : flags2list
  },
  'SCCSGETFLAGS' : {
      'help'        : 'Options that are passed specifically to the SCCS "get" subcommand',
      'metavar'     : 'FLAGS',
      'converter'   : flags2list
  },
}

_groups = {
    'progs' : [ 'SCCS' ],
    'flags' : [ 'SCCSFLAGS', 'SCCSGETFLAGS' ]
}

def arguments(**kw):
    """Returns argument declarations for 'sccs' tool

       :Keywords:
            include_groups : str | list
                include only arguments assigned to these groups
            exclude_groups : str | list
                exclude arguments assigned to these groups
            sccs_include_groups : str | list
                include only arguments assigned to these groups, this has
                higher priority than **include_groups**
            sccs_exclude_groups : str | list
                exclude arguments assigned to these groups, this has higher
                priority than **exclude_groups**
    """
    return export_arguments('sccs', _all_arguments, _groups, **kw)

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
