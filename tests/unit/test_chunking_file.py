import chunk
import os
from shutil import rmtree
from time import sleep

import pytest

from audiochunker import (
    AudioChunker
)

# This audio file is supposed to have 3 utterances and 4 silence periodes.
audio_3_utterances = 'tests/resources/audio_3_utterances.wav'

# This audio file is supposed to have 66 utterances and 67 silence periodes.
audio_66_utterances = 'tests/resources/audio_66_utterances.wav'


chunks_path = 'tests/resources/chunks'

# Inexistent audio file
inexistent_audio = 'tests/resources/inexistent.wav'

def setup():
    if os.path.exists(chunks_path):
        rmtree(chunks_path)
    sleep(1)
    os.mkdir(chunks_path)

def test_with_inexistent_audio_file():    
    with pytest.raises(FileNotFoundError):
        chunker = AudioChunker(inexistent_audio)
        _, _ = chunker.chunking_file()

def test_with_inexistent_chunks_path():    
    with pytest.raises(ValueError):
        chunker = AudioChunker(audio_3_utterances)
        _, _ = chunker.chunking_file()



def test_create_chunks():
    chunker = AudioChunker(audio_3_utterances)
    chunks, silences = chunker.chunking_file(chunks_path=chunks_path)

    assert chunks is not None
    assert silences is not None
    assert len(chunks) == 3
    assert len(silences) == 4
    assert os.path.exists(chunks[0].chunk_file_path)
    assert os.path.exists(chunks[1].chunk_file_path)
    assert os.path.exists(chunks[2].chunk_file_path)

def test_create_chunks_huge_file():
    chunker = AudioChunker(audio_66_utterances)
    chunks, silences = chunker.chunking_file(chunks_path=chunks_path)

    assert chunks is not None
    assert silences is not None
    assert len(chunks) == 66
    assert len(silences) == 67
    assert os.path.exists(chunks[0].chunk_file_path)
    assert os.path.exists(chunks[1].chunk_file_path)
    assert os.path.exists(chunks[2].chunk_file_path)
    assert os.path.exists(chunks[len(chunks)-1].chunk_file_path)
