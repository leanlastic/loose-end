from setuptools import setup, find_packages

setup(
    name='loose-end-cli',
    version='1.0',
    py_modules=['loose_end'],
    install_requires=[
        'typer[all]',
        'PyGithub',
    ],
    entry_points={
        'console_scripts': [
            'loose-end = loose_end:app',
        ],
    },
)
