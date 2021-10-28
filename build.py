from pybuilder.core import use_plugin
from pybuilder.core import init
from pybuilder.core import Author
from pybuilder.core import task

use_plugin('python.core')
use_plugin('python.unittest')
use_plugin('python.flake8')
use_plugin('python.coverage')
use_plugin('python.distutils')
use_plugin('pypi:pybuilder_radon')
use_plugin('pypi:pybuilder_bandit')
use_plugin('pypi:pybuilder_anybadge')

name = 'dockerhub-audit'
authors = [
    Author('Bill Mahoney', 'bill.mahoney@intel.com')]
summary = 'A Python script that audits all EdgeX Foundry Dockerhub images with a focus is on staleness and relevency.'
version = '0.0.2'
default_task = [
    'clean',
    'analyze',
    'publish',
    'radon',
    'bandit',
    'anybadge']


@init
def set_properties(project):
    project.set_property('unittest_module_glob', 'test_*.py')
    project.set_property('coverage_break_build', False)
    project.set_property('flake8_max_line_length', 120)
    project.set_property('flake8_verbose_output', True)
    project.set_property('flake8_break_build', True)
    project.set_property('flake8_include_scripts', True)
    project.set_property('flake8_include_test_sources', True)
    project.set_property('flake8_ignore', 'E501, F401, F403')
    project.build_depends_on_requirements('requirements-build.txt')
    project.depends_on_requirements('requirements.txt')
    project.set_property('distutils_console_scripts', ['dockerhub-audit = dha.cli:main'])
    project.set_property('radon_break_build_complexity_threshold', 12)
    project.set_property('radon_break_build_average_complexity_threshold', 4)
    project.set_property('bandit_break_build', True)
    project.set_property('anybadge_use_shields', True)
    project.set_property('anybadge_add_to_readme', True)
