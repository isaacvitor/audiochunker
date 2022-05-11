import logging
import os
import subprocess
from tempfile import mkstemp
from typing import List


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


class AudioChunk:
    def __init__(self, file: str = None, file_size: str = None, start: int = 0, end: int = 0, duration: float = 0, text: str = None):
        self.file = file
        self.file_size = file_size
        self.start = start
        self.end = end
        self.duration = duration
        self.text = text
        self.conf = 1.0
    
    def __repr__(self):
        return f'file:{self.file} size:{self.file_size} start:{self.start} end:{self.end} duration:{self.duration} text:{self.text}'


class AudioFileChunker:
    def __init__(self, input_file_path=None, chunks_path=None, chunk_suffix='chunk_', silence_threshold=-30, silence_duration=0.5):   
        self.input_file_path = input_file_path
        self.chunks_path = chunks_path

        self.chunk_suffix = chunk_suffix
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration

        self.chunks: List[AudioChunk] = []
        self.silences = []
        self.commands = []
        self.big_command = ''
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        
    def __get_chunk_size(self):
        try:
            for chunk in self.chunks:
                if os.path.exists(chunk.file):
                    chunk.file_size = os.path.getsize(chunk.file)
                else:
                    logger.warning(f'File {chunk.file} does not exist')
        except Exception as e:
            raise e 


    def chunking(self,input_file_path = None, chunks_path=None, chunk_suffix=None):
        
        if input_file_path is None and self.input_file_path is None:
            raise Exception('input_file_path was not specified')
        input_file_path = self.input_file_path if input_file_path is None else input_file_path
        
        if not os.path.isfile(input_file_path):
            raise FileNotFoundError('input_file_path must be a audio file')

        if chunks_path is None and self.chunks_path is None:
            raise ValueError('chunks_path was not specified and must be a directory')
            
        
        chunks_path = self.chunks_path if chunks_path is None else chunks_path
        if not os.path.isdir(chunks_path):
            raise Exception('chunks_path must be a directory')

        try:
            # Getting silences times
            silence_file = FFMPEGTools.create_silence_file(input_file_path, self.silence_threshold, self.silence_duration)
            self.silences =  FFMPEGTools.get_silences_form_file(silence_file)
               
            chunk_suffix = self.chunk_suffix if chunk_suffix is None else chunk_suffix
            chunk_count = 0
            for s in range(0, len(self.silences)):
                tms = self.silences[s:s+2]        
                if len(tms) == 2:
                    t1 = tms[0]['end'] - 0.25
                    t2 = tms[1]['start'] - tms[0]['end'] + 3 * 0.25
                    chunk_name = f'{chunk_suffix}{chunk_count}.wav'
                    chunk_path = os.path.join(chunks_path, chunk_name)
                    __command = f'ffmpeg -v error -y -ss {t1} -t {t2} -i {input_file_path} {chunk_path}'
                    self.commands.append(__command)
                    self.big_command += __command + ' & '
                    self.chunks.append(AudioChunk(file=chunk_path, file_size=0, start=t1, end=t2+t1, duration=t2, text=None))
                chunk_count += 1

            subprocess.check_output(self.big_command, shell=True)
            self.__get_chunk_size()
            return (self.chunks, self.silences)
        except Exception as e:
            raise e
