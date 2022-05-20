import os
from shutil import rmtree
from time import sleep

import pytest
from pydub import AudioSegment

from audiochunker import (
    AudioChunker,
    SegmentChunk
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
        chunker = AudioChunker(inexistent_audio)
        _, _ = chunker.chunking_segment()

def test_with_inexistent_chunks_path():    
    with pytest.raises(ValueError):
        chunker = AudioChunker(audio_3_utterances)
        _, _ = chunker.chunking_segment()

def test_chunk_interator():
    chunker = AudioChunker(audio_3_utterances)
    chunks_iter = chunker.chunking_segment()
    assert type(next(chunks_iter)) == SegmentChunk
    assert next(chunks_iter).audio_segment.raw_data != None

    chunk_path = os.path.join(chunks_path, 'chunk_iter.wav')
    next(chunks_iter).audio_segment.export(chunk_path, format='wav')
    assert os.path.exists(chunk_path)

    with pytest.raises(StopIteration):
        no_chunk = next(chunks_iter)