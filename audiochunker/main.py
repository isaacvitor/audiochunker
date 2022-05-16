import logging
import os
import subprocess
from tempfile import mkstemp
from typing import List, Tuple

from pydub import AudioSegment


logger = logging.getLogger('scribezilla-service')

class FFMPEGTools:
    """
    FFMPEGTools class.
    """
    
    def __get_start_time(time_str):
        if 'silence_start' in time_str:
            t = time_str.split('silence_start:')[1] 
            return {'start': float(t)}
    
    def __get_end_time(time_str):
        if 'silence_end' in time_str:
            times = time_str.split(' | ')
            se = float(times[0].split('silence_end: ')[1])
            sd = float(times[1].split('silence_duration: ')[1])
            return {'end':se, 'duration':sd}

    @staticmethod
    def create_silence_file(audio_path: str, silence_threshold=-30, silence_duration=0.5) -> str:
        """
        Create silence file.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f'Audio file {audio_path} not found.')
            
        silence_file = mkstemp(suffix='_times', prefix='silences_', dir=None, text=True)
        _, silence_path_file = silence_file 
        if audio_path is None:
            raise ValueError('audio_path is not set.')

        if silence_threshold is None:
            raise ValueError('silence_threshold is not set.')
        
        if silence_duration is None:
            raise ValueError('silence_duration is not set.')

        times_command = f'ffmpeg -i {audio_path} -af silencedetect=noise={silence_threshold}dB:d={silence_duration} -f null - 2> {silence_path_file}'
        subprocess.check_output(times_command, shell=True)

        return silence_path_file

    @classmethod
    def get_silences_form_file(cls, silence_path_file: str) -> list:
        """
        Get silences from a audio file.
        """
        if silence_path_file is None:
                raise ValueError('silence_path_file was not specified')

        try:
            silences = []

            with open(silence_path_file, 'r') as f:
                lines = f.readlines()
                times = []
                for line in lines:
                    if 'silencedetect' in line:
                        line_str = line.split('] ')[1].strip()
                        if 'silence_start' in line_str:
                            times.append(cls.__get_start_time(line_str))
                        elif 'silence_end' in line_str:
                            times.append(cls.__get_end_time(line_str))

                for i in range(0, len(times), 2):
                    silence = times[i:i+2]
                    silences.append({**silence[0], **silence[1]})
            return silences            
        except Exception as e:
            raise e
        finally:
            os.remove(silence_path_file)


class BaseChunk:
    def __init__(self, **kwargs):
        self.content_size: float = kwargs.get('content_size', 0)
        self.start: float = kwargs.get('start', 0)
        self.end: float = kwargs.get('end', 0)
        self.start_milliseconds = self.start * 1000
        self.end_milliseconds = self.end * 1000
        self.duration: float = kwargs.get('duration', 0)        
        self.conf = 1.0
        self.text: str = kwargs.get('text', None)
    
    def __repr__(self):
        return f'start:{self.start} end:{self.end} duration:{self.duration} content_size:{self.content_size} text:{self.text}'


class SegmentChunk(BaseChunk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)        
        self.audio_segment: AudioSegment = kwargs.get('audio_segment', None) 
        if self.audio_segment is not None:
            self.content_size = len(self.audio_segment.raw_data)
        self.__dict__.update(kwargs)


class FileChunk(BaseChunk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chunk_file_path: str = kwargs.get('chunk_file_path', None)
        self.__dict__.update(kwargs)
    
    def __repr__(self):
        return f'chunk_file_path:{self.chunk_file_path}, start:{self.start} end:{self.end} duration:{self.duration} content_size:{self.content_size} text:{self.text}'


class AudioChunker:
    def __init__(self, input_file_path, silence_threshold=-30, silence_duration=0.5):
        if input_file_path is None:
            raise ValueError('input_file_path is not set.')

        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f'Audio file {input_file_path} not found.')

        self.input_file_path = input_file_path
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration

        self.chunks: List[BaseChunk] = []
        
        silence_file = FFMPEGTools.create_silence_file(self.input_file_path, self.silence_threshold, self.silence_duration)
        self.silences =  FFMPEGTools.get_silences_form_file(silence_file)

    def __create_chunks_from_silences(self, silences: List[dict])-> List[BaseChunk]:
        try:
            chunks_times = []
            for silence in range(0, len(self.silences)):
                tms = self.silences[silence:silence+2]        
                if len(tms) == 2:
                    t1 = tms[0]['end'] - 0.25
                    t2 = tms[1]['start'] - tms[0]['end'] + 3 * 0.25
                    chunks_times.append(BaseChunk(start=t1, end=t2+t1, duration=t2))
            return chunks_times
        except Exception as e:
            raise e

    def chunking_segment(self) -> SegmentChunk:     
        audio_segment = AudioSegment.from_wav(self.input_file_path)
        chunk_times = self.__create_chunks_from_silences(self.silences)
        for chunk in chunk_times:
            yield SegmentChunk(**chunk.__dict__, audio_segment=audio_segment[chunk.start_milliseconds:chunk.end_milliseconds])

    def chunking_file(self, chunks_path=None, chunk_suffix='chunk_') -> tuple:
        if chunks_path is None:
            raise ValueError('chunks_path was not specified and must be a directory')             
       
        if not os.path.isdir(chunks_path):
            raise Exception('chunks_path must be a directory')

        try:
            audio_segment = AudioSegment.from_wav(self.input_file_path)
            chunk_times: List[BaseChunk] = self.__create_chunks_from_silences(self.silences)
            chunk_count:int = 0
            chunk: BaseChunk
            for chunk in chunk_times:
                chunk_name = f'{chunk_suffix}{chunk_count}.wav'
                chunk_path = os.path.join(chunks_path, chunk_name)
                # Export
                segment = audio_segment[chunk.start_milliseconds:chunk.end_milliseconds]
                segment.export(chunk_path, format='wav')
                chunk.content_size = len(segment.raw_data)
                self.chunks.append(FileChunk(**chunk.__dict__, chunk_file_path=chunk_path))
                chunk_count += 1
            
            return (self.chunks, self.silences)
        except Exception as e:
            raise e
