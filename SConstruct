#!/usr/bin/env python3

import sys
import os
import os.path
import glob
import re


if sys.version_info < (3,):
    def isbasestring(s):
        return isinstance(s,basestring)
else:
    def isbasestring(s):
        return isinstance(s, (str,bytes))

def add_kel_source_files(self, sources, filetype, lib_env=None, shared=False, target_post=""):

    if isbasestring(filetype):
        dir_path = self.Dir('.').abspath
        filetype = sorted(glob.glob(dir_path+"/"+filetype))

    for path in filetype:
        target_name = re.sub( r'(.*?)(\.cpp|\.c\+\+)', r'\1' + target_post, path )
        if shared:
            target_name+='.os'
            sources.append( self.SharedObject( target=target_name, source=path ) )
        else:
            target_name+='.o'
            sources.append( self.StaticObject( target=target_name, source=path ) )
    pass

def isAbsolutePath(key, dirname, env):
	assert os.path.isabs(dirname), "%r must have absolute path syntax" % (key,)

env_vars = Variables(
	args=ARGUMENTS
)

env_vars.Add('prefix',
	help='Installation target location of build results and headers',
	default='/usr/local/',
	validator=isAbsolutePath
)

env=Environment(ENV=os.environ, variables=env_vars, CPPPATH=[],
    CPPDEFINES=['SAW_UNIX'],
    CXXFLAGS=['-std=c++20','-g','-Wall','-Wextra'],
    LIBS=['forstio-core','forstio-codec'])
env.__class__.add_source_files = add_kel_source_files
env.Tool('compilation_db');
env.cdb = env.CompilationDatabase('compile_commands.json');

env.objects = [];
env.sources = [];
env.headers = [];
env.targets = [];

Export('env')
SConscript('c++/SConscript')

env.Alias('cdb', env.cdb);
env.Alias('all', [env.targets]);
env.Default('all');

env.Alias('install', '$prefix')
