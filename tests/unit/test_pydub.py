import os
from shutil import rmtree
from time import sleep

import pytest
from pydub import AudioSegment

from audiochunker.main import (
    AudioFileChunker,
    AudioChunk
)


# This audio file is supposed to have 3 utterances and 4 silence periodes.
audio_3_utterances = 'tests/resources/audio_3_utterances.wav'

# This audio file is supposed to have 66 utterances and 67 silence periodes.
audio_66_utterances = 'tests/resources/audio_66_utterances.wav'


chunks_path = 'tests/resources/chunks'


def setup():
    if os.path.exists(chunks_path):
        rmtree(chunks_path)
    sleep(1)
    os.mkdir(chunks_path)


# Inexistent audio file
inexistent_audio = 'tests/resources/inexistent.wav'


def test_with_inexistent_audio_file():
    with pytest.raises(FileNotFoundError):
        chunker = AudioFileChunker(inexistent_audio)
        _, _ = chunker.chunking()

def test_with_inexistent_chunks_path():    
    with pytest.raises(ValueError):
        chunker = AudioFileChunker(audio_3_utterances)
        _, _ = chunker.chunking()



def test_create_chunks():
    chunker = AudioFileChunker(audio_3_utterances, chunks_path=chunks_path)
    chunks, silences = chunker.chunking()

    assert chunks is not None
    assert silences is not None
    assert len(chunks) == 3
    assert len(silences) == 4
    assert os.path.exists(chunks[0].file)
    assert os.path.exists(chunks[1].file)
    assert os.path.exists(chunks[2].file)

def test_create_chunks_huge_file():
    chunker = AudioFileChunker(audio_66_utterances, chunks_path=chunks_path)
    chunks, silences = chunker.chunking()

    assert chunks is not None
    assert silences is not None
    assert len(chunks) == 66
    assert len(silences) == 67
    assert os.path.exists(chunks[0].file)
    assert os.path.exists(chunks[1].file)
    assert os.path.exists(chunks[2].file)
    assert os.path.exists(chunks[len(chunks)-1].file)


def test_chunk_interator():
    chunker = AudioFileChunker(audio_3_utterances)
    chunks_iter = chunker.chunking_interator()
    assert type(next(chunks_iter)) == AudioChunk
    assert next(chunks_iter).audio_segment.raw_data != None

    chunk_path = os.path.join(chunks_path, 'chunk_iter.wav')
    next(chunks_iter).audio_segment.export(chunk_path, format='wav')
    assert os.path.exists(chunk_path)

    with pytest.raises(StopIteration):
        no_chunk = next(chunks_iter)