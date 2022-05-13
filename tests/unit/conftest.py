import os
from shutil import rmtree

chunks_path = 'tests/resources/chunks'


def pytest_sessionstart(session):
    if os.path.exists(chunks_path):
        rmtree(chunks_path)
    
    os.mkdir(chunks_path)  


def pytest_sessionfinish(session, exitstatus):    
    if os.path.exists(chunks_path):
        rmtree(chunks_path)