from setuptools import Extension, setup, find_packages
from glob import glob
import os, sys

project_name = 'someip_adapter'
script_directory = os.path.realpath(os.path.dirname(__file__))

is_windows = sys.platform.startswith('win')
windows_vsomeip_path = os.path.join(script_directory, 'cots', 'vsomeip')

# reference: https://setuptools.pypa.io/en/latest/userguide/ext_modules.html
extension_path = os.path.relpath(os.path.join(project_name, 'vsomeip_extension'))
vsomeip_extension = Extension('vsomeip_ext',
                      include_dirs=['/usr/local/include/' if not is_windows else os.path.join(windows_vsomeip_path, 'include')],
                      sources=[os.path.join(extension_path, 'vsomeip.cpp')],
                      libraries=['vsomeip3', 'vsomeip3-cfg'],
                      library_dirs=['/usr/local/lib/' if not is_windows else os.path.join(windows_vsomeip_path, 'lib')],
                      extra_compile_args = ['-std=c++14'] if not is_windows else ['-DWIN32', '/std:c++14', '/MD', '/EHsc', '/wd4250'],
                      runtime_library_dirs=['/usr/local/lib/'] if not is_windows else [])

setup(
    name=project_name,
    version='0.5',
    python_requires='>=3.8',
    description='',
    author='',
    author_email='',
    data_files=[],
    packages=find_packages(exclude=['**/*.cpp']),
    include_package_data=True,  # see MANIFEST.in
    dependency_links=[],
    install_requires=[],
    cmdclass={},
    license='LICENSE.txt',
    long_description=open('README.md').read(),
    ext_modules=[vsomeip_extension],
)
