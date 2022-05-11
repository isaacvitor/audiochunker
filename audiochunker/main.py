import os
import subprocess
from tempfile import mkstemp


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
