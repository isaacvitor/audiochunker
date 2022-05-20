from setuptools import find_packages, setup

setup(
    name='audiochunker',
    packages=find_packages(include=['audiochunker']),
    version='0.1.3',
    description='Python library for chunking audio',
    author='Isaac Vitor',
    license='MIT',
    url="https://github.com/isaacvitor/audiochunker",
    project_urls={
        "Bug Tracker": "https://github.com/isaacvitor/audiochunker/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pydub==0.25.1'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==7.1.2'],
    test_suite='tests',
)