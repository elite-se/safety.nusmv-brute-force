from setuptools import find_packages, setup

setup(
    name='nuSMV-brute-force',
    packages=['util'],
    scripts=['nusmv-brute-force'],
    version='0.1.0',
    description='wrapper for nusmv which concurrently execute nusmv so that its faster',
    author='roanbu',
    license='MIT',
    install_requires=[
        
    ]
)
