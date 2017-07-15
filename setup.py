#!/usr/bin/env python
import os
from codecs import open
from distutils.command.build import build as _build

import setuptools
from setuptools import setup, find_packages
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg

import apkid

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


def package_files(directory):
    paths = []
    for (filepath, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(filepath, filename))
    return paths


class bdist_egg(_bdist_egg):
    def run(self):
        self.run_command('build_yarac')
        _bdist_egg.run(self)


class build_yarac(setuptools.Command):
    description = 'compile Yara rules'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import yara
        import fnmatch
        rules_dir = 'apkid/rules/'
        compiled_rules_path = os.path.join(rules_dir, 'rules.yarc')

        yara_files = {}
        for root, dirnames, filenames in os.walk(rules_dir):
            for filename in fnmatch.filter(filenames, '*.yara'):
                path = os.path.join(root, filename)
                yara_files[path] = path
        print("Compiling {} Yara rule files".format(len(yara_files)))
        rules = yara.compile(filepaths=yara_files)
        rules.save(compiled_rules_path)
        # Note: Can only enumerate rules once
        count = sum(1 for _ in rules)
        print("Saved {} rules to {}".format(count, compiled_rules_path))


class build(_build):
    sub_commands = _build.sub_commands + [('build_yarac', None)]


class update(setuptools.Command):
    description = "prepare for release (only used by maintainers)"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import pypandoc
        import codecs
        print("Converting Markdown README to reStructuredText")
        rst = pypandoc.convert_file('README.md', 'rst')
        with codecs.open('README.rst', 'w+', encoding='utf-8') as f:
            f.write(rst)
        print("Finished converting to README.rst ({} bytes)".format(len(rst)))


install_requires = [
    'yara-python==3.6.0.999',
    'argparse',
]

setup(
    name=apkid.__title__,
    version=apkid.__version__,
    description="Android Package Identifier",
    long_description=long_description,
    url='https://github.com/rednaga/APKiD',
    author=apkid.__author__,
    author_email='rednaga@protonmail.com',
    license=apkid.__license__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security',
        'Topic :: Utilities',
    ],
    cmdclass={
        'bdist_egg': bdist_egg,
        'build': build,
        'build_yarac': build_yarac,
        'update': update,
    },
    keywords='android analysis reversing malware apk dex',
    packages=find_packages('.', exclude=['docs', 'tests']),
    package_data={
        'rules': package_files('apkid/rules/'),
    },
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=[
        'https://github.com/rednaga/yara-python/zipball/360_test#egg=yara-python-3.6.0.999'
    ],
    extras_require={
        'dev': [
            'pypandoc'
        ],
        'test': [],
    },
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'apkid=apkid:main',
        ],
    },
)
