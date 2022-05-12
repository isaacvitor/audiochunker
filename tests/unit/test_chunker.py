import chunk
import os

import pytest

from audiochunker.main import (
    FFMPEGTools,
    AudioFileChunker
)

# This audio file is supposed to have 3 utterances and 4 silence periodes.
audio_3_utterances = 'tests/resources/audio_3_utterances.wav'

# This audio file is supposed to have 66 utterances and 67 silence periodes.
audio_66_utterances = 'tests/resources/audio_66_utterances.wav'


chunks_path = 'tests/resources/chunks'

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
    

# def test_get_silences():
#     silence_file = FFMPEGTools.create_silence_file(audio_3_utterances)
#     silences = FFMPEGTools.get_silences_form_file(silence_file)
    
#     assert silences != None
#     assert len(silences) == 4
#     assert os.path.exists(silence_file) == False