import os

import pytest

from audiochunker.main import (
    FFMPEGTools
)

# This audio file has is supposed to have 3 utterances and 4 silence periodes.
audio_16k = 'tests/resources/test16k.wav'

# Inexistent audio file
inexistent_audio = 'tests/resources/inexistent.wav'

def test_with_inexistent_audio_file():    
    with pytest.raises(FileNotFoundError):
        silence_file = FFMPEGTools.create_silence_file(inexistent_audio)

def test_with_inexistent_silence_file():    
    with pytest.raises(FileNotFoundError):
        silence_file = FFMPEGTools.get_silences_form_file(inexistent_audio)


def test_create_silence_file():
    audio_path = audio_16k
    silence_threshold = -30
    silence_duration = 0.5
    silence_file = FFMPEGTools.create_silence_file(audio_path, silence_threshold, silence_duration)

    assert silence_file is not None
    assert os.path.exists(silence_file)
    os.remove(silence_file)


def test_get_silences():
    silence_file = FFMPEGTools.create_silence_file(audio_16k)
    silences = FFMPEGTools.get_silences_form_file(silence_file)
    
    assert silences != None
    assert len(silences) == 4
    assert os.path.exists(silence_file) == False