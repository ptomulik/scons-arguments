#
# Copyright (c) 2012-2017 by Pawel Tomulik
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

"""
Tests declaring variables with SConsArguments.DeclareArguments()
"""

import TestSCons

##############################################################################
# DeclareArguments(): Test 2
##############################################################################
test = TestSCons.TestSCons()
test.dir_fixture('../../../SConsArguments', 'site_scons/SConsArguments')
test.write('SConstruct',
"""
# SConstruct
import SConsArguments
x = { 'env_key' : 'env_x' , 'var_key' : 'var_x', 'opt_key' : 'opt_x', 'default' : 'x default', 'option' : '-x' }
y = { 'env_key' : 'env_y' , 'var_key' : 'var_y', 'opt_key' : 'opt_y', 'default' : 'y default', 'option' : '-y' }
list = []
list.append( SConsArguments.DeclareArguments(x = x, y = y) )
list.append( SConsArguments.DeclareArguments({'x' : x, 'y' : y}) )
i = 0
for v in list:
    for c in ['x', 'y']:
        print("ARGS[%d][%r].has_decl(ENV): %r" % (i, c, v[c].has_decl(SConsArguments.ENV)))
        print("ARGS[%d][%r].has_decl(VAR): %r" % (i, c, v[c].has_decl(SConsArguments.VAR)))
        print("ARGS[%d][%r].has_decl(OPT): %r" % (i, c, v[c].has_decl(SConsArguments.OPT)))
        print("ARGS[%d][%r].get_key(ENV): %r" % (i, c, v[c].get_key(SConsArguments.ENV)))
        print("ARGS[%d][%r].get_key(VAR): %r" % (i, c, v[c].get_key(SConsArguments.VAR)))
        print("ARGS[%d][%r].get_key(OPT): %r" % (i, c, v[c].get_key(SConsArguments.OPT)))
        print("ARGS[%d][%r].get_default(ENV): %r" % (i, c, v[c].get_default(SConsArguments.ENV)))
        print("ARGS[%d][%r].get_default(VAR): %r" % (i, c, v[c].get_default(SConsArguments.VAR)))
        print("ARGS[%d][%r].get_default(OPT): %r" % (i, c, v[c].get_default(SConsArguments.OPT)))
    i += 1
""")
test.run()

lines = [
        "ARGS[0]['x'].has_decl(ENV): True",
        "ARGS[0]['x'].has_decl(VAR): True",
        "ARGS[0]['x'].has_decl(OPT): True",
        "ARGS[0]['x'].get_key(ENV): 'env_x'",
        "ARGS[0]['x'].get_key(VAR): 'var_x'",
        "ARGS[0]['x'].get_key(OPT): 'opt_x'",
        "ARGS[0]['x'].get_default(ENV): 'x default'",
        "ARGS[0]['x'].get_default(VAR): 'x default'",
        "ARGS[0]['x'].get_default(OPT): UNDEFINED",

        "ARGS[0]['y'].has_decl(ENV): True",
        "ARGS[0]['y'].has_decl(VAR): True",
        "ARGS[0]['y'].has_decl(OPT): True",
        "ARGS[0]['y'].get_key(ENV): 'env_y'",
        "ARGS[0]['y'].get_key(VAR): 'var_y'",
        "ARGS[0]['y'].get_key(OPT): 'opt_y'",
        "ARGS[0]['y'].get_default(ENV): 'y default'",
        "ARGS[0]['y'].get_default(VAR): 'y default'",
        "ARGS[0]['y'].get_default(OPT): UNDEFINED",

        "ARGS[1]['x'].has_decl(ENV): True",
        "ARGS[1]['x'].has_decl(VAR): True",
        "ARGS[1]['x'].has_decl(OPT): True",
        "ARGS[1]['x'].get_key(ENV): 'env_x'",
        "ARGS[1]['x'].get_key(VAR): 'var_x'",
        "ARGS[1]['x'].get_key(OPT): 'opt_x'",
        "ARGS[1]['x'].get_default(ENV): 'x default'",
        "ARGS[1]['x'].get_default(VAR): 'x default'",
        "ARGS[1]['x'].get_default(OPT): UNDEFINED",

        "ARGS[1]['y'].has_decl(ENV): True",
        "ARGS[1]['y'].has_decl(VAR): True",
        "ARGS[1]['y'].has_decl(OPT): True",
        "ARGS[1]['y'].get_key(ENV): 'env_y'",
        "ARGS[1]['y'].get_key(VAR): 'var_y'",
        "ARGS[1]['y'].get_key(OPT): 'opt_y'",
        "ARGS[1]['y'].get_default(ENV): 'y default'",
        "ARGS[1]['y'].get_default(VAR): 'y default'",
        "ARGS[1]['y'].get_default(OPT): UNDEFINED",
]

test.must_contain_all_lines(test.stdout(), lines)

test.pass_test()

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
