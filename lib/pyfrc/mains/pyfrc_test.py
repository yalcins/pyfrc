
import os
import sys
import inspect

from os.path import abspath, dirname, exists, join

import pytest

from pyfrc.support import pyfrc_hal_hooks, fake_time

from hal_impl import data, functions

from hal_impl import pwm_helpers as pwm_help_funcs
from hal_impl import mode_helpers as mode_help_funcs

# TODO: setting the plugins so that the end user can invoke py.test directly
# could be a useful thing. Will have to consider that later.

class PyFrcPlugin(object):

    def __init__(self, robot, file_location, hooks):
        self.robot_inst = robot
        self.file_location = file_location
        self.hooks = hooks
    
    def pytest_runtest_setup(self):
        '''Runs autonomous mode by itself'''
        fake_time.FAKETIME.reset()
        robot = robot_class()
        data.hal_data['control']['enabled'] = True
        data.hal_data['control']['ds_attached'] = True
        data.hal_data['control']['fms_attached'] = True

    
    #
    # Fixtures
    #
    # Each one of these can be arguments to your test, and the result of the
    # corresponding function will be passed to your test as that argument.
    #
    
    @pytest.fixture()
    def hal_hooks(self):
        return self.hooks
    
    @pytest.fixture()
    def fake_time(self):
        return fake_time.FAKETIME
    
    @pytest.fixture()
    def robot(self):
        return self.robot_inst
    
    @pytest.fixture()
    def robot_path(self):
        return file_location
    
    @pytest.fixture()
    def hal_map(self):
        return data.hal_data
    
    @pytest.fixture()
    def pwm_helpers(self):
        return pwm_help_funcs
    
    @pytest.fixture()
    def mode_helpers(self):
        return mode_help_funcs

#
# main test class
#
class PyFrcTest(object):
    
    def __init__(self, parser):
        parser.add_argument('pytest_args', nargs='*',
                            help="To pass args to pytest, specify --, then the args")
    
    def run(self, options, robot_class):
    
        # find test directory, change current directory so py.test can find the tests
        # -> assume that tests reside in tests or ../tests
        test_directory = None
        
        root = abspath(os.getcwd())
        
        try_dirs = [join(root, 'tests'), abspath(join(root, '..', 'tests'))]
        
        for d in try_dirs:
            if exists(d):
                test_directory = d
                break
        
        if test_directory is None:
            print("Cannot run robot tests, as test directory was not found. Looked for tests at:")
            for d in try_dirs:
                print('- %s' % d)
            return 1
        
        os.chdir(test_directory)
        file_location = abspath(inspect.getfile(robot_class))
        
        self.hooks = pyfrc_hal_hooks.PyFrcSimHooks(fake_time.FAKETIME)
        
        functions.hooks = self.hooks
        data.reset_hal_data(self.hooks)
        
        robot = robot_class()
        return pytest.main(options.pytest_args, plugins=[PyFrcPlugin(robot, file_location, self.hooks)])

