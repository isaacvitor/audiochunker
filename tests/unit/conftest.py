import logging
import os
from shutil import rmtree

logger = logging.getLogger(__name__)

chunks_path = 'tests/resources/chunks'

def pytest_sessionstart(session):
    print('Session start')
    if os.path.exists(chunks_path):
        rmtree(chunks_path)
    
    os.mkdir(chunks_path)  


def pytest_sessionfinish(session, exitstatus):
    print('\nSession finish')
    if os.path.exists(chunks_path):
        rmtree(chunks_path)