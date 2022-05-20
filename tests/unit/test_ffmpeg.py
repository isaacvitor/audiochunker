import os

import pytest

from audiochunker import (
    FFMPEGTools, FFMPEGException
)

# This audio file is supposed to have 3 utterances and 4 silence periodes.
audio_3_utterances = 'tests/resources/audio_3_utterances.wav'
reference_silence_file = 'tests/resources/silence_reference'

# Inexistent audio file
inexistent_audio = 'tests/resources/inexistent.wav'

# Invalid wav file
invalid_wav = 'tests/resources/error.wav'

empty_file = 'tests/resources/empty_file.txt'

def test_with_inexistent_audio_file():    
    with pytest.raises(FileNotFoundError):
        FFMPEGTools.create_silence_content(inexistent_audio)

def test_with_inexistent_silence_file():    
    with pytest.raises(ValueError):
        FFMPEGTools.get_silences_from_file(None)

def test_invalid_silence_file():    
    with pytest.raises(FFMPEGException):
        FFMPEGTools.get_silences_from_file(inexistent_audio)

def test_no_silence_threshold():    
    with pytest.raises(ValueError):
        FFMPEGTools.create_silence_content(audio_3_utterances, silence_threshold=None)

def test_no_silence_duration():    
    with pytest.raises(ValueError):
        FFMPEGTools.create_silence_content(audio_3_utterances, silence_duration=None)

def test_ffmpeg_exception():    
    with pytest.raises(FFMPEGException):
        FFMPEGTools.create_silence_content(reference_silence_file)

def test_invalid_wav():    
    with pytest.raises(FFMPEGException):
        FFMPEGTools.create_silence_file(invalid_wav)

def test_create_silence_content():
    audio_path = audio_3_utterances
    silence_threshold = -30
    silence_duration = 0.5
    silence_content = FFMPEGTools.create_silence_content(audio_path, silence_threshold, silence_duration)

    lines = silence_content.splitlines()
    start_match = False
    end_match = False

    assert silence_content is not None
    assert len(silence_content) > 0
   
    for line in lines:
        if 'silence_start' in line:
            start_match = True
        if 'silence_end' in line:
            end_match = True
    assert start_match
    assert end_match

def test_create_silence_file():
    audio_path = audio_3_utterances
    silence_threshold = -30
    silence_duration = 0.5
    silence_file_path = FFMPEGTools.create_silence_file(audio_path, silence_threshold, silence_duration)

    start_match = False
    end_match = False
    
    assert silence_file_path is not None
    with open(silence_file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'silence_start' in line:
                start_match = True
            if 'silence_end' in line:
                end_match = True
    assert start_match
    assert end_match
    

def test_get_silences_file():
    silence_file_path = FFMPEGTools.create_silence_file(audio_3_utterances)
    silences = FFMPEGTools.get_silences_from_file(silence_file_path)
    reference = FFMPEGTools.get_silences_from_file(reference_silence_file)
    
    assert silences != None
    assert len(silences) == 4
    assert silences == reference

def test_get_silences_content():
    silence_content = FFMPEGTools.create_silence_content(audio_3_utterances)
    silences = FFMPEGTools.get_silences_from_content(silence_content)
    reference = FFMPEGTools.get_silences_from_file(reference_silence_file)
    
    assert silences != None
    assert len(silences) == 4
    assert silences == reference

def test_is_a_valid_silence_file():
    valid_path = FFMPEGTools.create_silence_file(audio_3_utterances)

    assert FFMPEGTools.is_valid_silence_file(valid_path)
    assert FFMPEGTools.is_valid_silence_file(empty_file) is False