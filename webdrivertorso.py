#!coding:utf-8
"""
webdrivertorso.py - A humble homage to the original Webdriver Torso 
YouTube channel
"""
__author__ = u'Moisés Cachay Tello'
__copyright__ = u'Copyright 2014, Moisés Cachay Tello'

from datetime import datetime
from itertools import *
from math import pi, sin
from os import makedirs, chdir
from random import randint, choice
from string import printable
from shutil import rmtree
import argparse
import subprocess
import struct
import time
import wave

from PIL import Image, ImageDraw, ImageFont


class ImageGenerator(object):
    """Image generation class. Uses Pillow to create a series of PNG images."""

    def __init__(self, image_size, rectangle_colors, background_color, 
                 text, font_name, text_color):
        self.image_size = image_size
        self.rectangle_colors = rectangle_colors
        self.background_color = background_color
        self.text = text
        self.font = ImageFont.truetype(font_name, int(image_size[1] * .03))
        self.text_color = text_color

    def get_image(self, number):
        image = Image.new('RGB', self.image_size)
        pen = ImageDraw.Draw(image)
        pen.rectangle([(0, 0), self.image_size], fill=self.background_color)
        
        for color in self.rectangle_colors:
            pen.rectangle(
                [(randint(0, self.image_size[0]), randint(0, self.image_size[1])),
                 (randint(0, self.image_size[0]), randint(0, self.image_size[1]))],
                fill=color
            )

        pen.text((self.image_size[0] * .015, self.image_size[1] * .95), 
                 self.text.format(number),
                 fill=self.text_color, 
                 font=self.font)

        del pen
        return image

    @staticmethod
    def save_image(image, path):
        image.save(path, 'PNG')


class SoundGenerator(object):
    """
    Sound generation class. A poor rip from 
    http://zacharydenton.com/generate-audio-with-python/ and the base of
    Zachary's WaveBender Library.
    """
    
    # WARNING: VERY ugly python code ahead, however it's worth the amazing
    # use of itertools to generate these random wavefiles.
    
    def sine_wave(self, frequency=440.0, framerate=44100, amplitude=1.0, 
                  skip_frame=0):
        if amplitude > 1.0: amplitude = 1.0
        if amplitude < 0.0: amplitude = 0.0
        for i in count(skip_frame):
            sine = sin(2.0 * pi * float(frequency) * (float(i) / float(framerate)))
            yield float(amplitude) * sine

    def compute_samples(self, channels, nsamples=None):
        return islice(izip(*(imap(sum, izip(*channel))
                             for channel in channels)), nsamples)

    @staticmethod
    def grouper(n, iterable, fillvalue=None):
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)

    @classmethod
    def write_wavefile(cls, filename, samples, nframes=None, nchannels=2,
                       sampwidth=2, framerate=44100, bufsize=2048):
        if nframes is None:
            nframes = -1
        
        # For some reason I cannot conceive, in some systems, the standard 
        # python library wave module doesn't work properly. A failsafe copy is
        # provided with this file.
        w = wave.open(filename, 'w')
        w.setparams((nchannels, sampwidth, framerate, nframes, 'NONE',
                     'not compressed'))

        max_amplitude = float(int((2 ** (sampwidth * 8)) / 2) - 1)

        for chunk in cls.grouper(bufsize, samples):
            frames = ''.join(''.join(struct.pack('h', int(max_amplitude * sample)) for sample in channels) for channels in chunk if channels is not None)
            w.writeframesraw(frames)
        
        w.close()

    def get_samples(self, frequency):
        channels = ((self.sine_wave(frequency, amplitude=.3),),)
        return self.compute_samples(channels, 44100 * 1)

    @classmethod
    def save_sound(cls, samples, path):
        cls.write_wavefile(path, samples, nchannels=1)


class VideoGenerator(object):
    """
    Video generation class. A simple wrapper to use the command line version
    of ffmpeg. A vanilla ffmpeg with libx264 would work (it must be present in
    system's PATH).
    """

    def __init__(self, file_format, soundfile, slide_number, output_file):
        self.file_format = file_format
        self.soundfile = soundfile
        self.slide_number = slide_number
        self.output_file = output_file

    def generate(self):

        # Generate an output of rate 1fps using the desired format and codec
        # for a given number of frames
        subprocess.call(
            'ffmpeg -r 1 -i %s -i %s '
            '-c:v libx264 -r %i -pix_fmt yuv420p %s' % 
            (self.file_format, self.soundfile, self.slide_number + 1, 
             self.output_file),
            shell=True
        )


class VideoUploader(object):
    """
    Video uploading class. A simple wrapper to use the command line version
    of youtube-upload, besides requiring the gdata package (and pycurl
    optionally), nothing special is required.
    """

    def __init__(self, email, password, title, filename):
        self.email = email
        self.password = password
        self.title = title
        self.filename = filename

    def upload(self):

        # Upload a given video for the channel with the given access details,
        # in the People category with a given title.
        subprocess.call(
            'youtube-upload --email=%s --password="%s" --category=People '
            '--title="%s" %s' % (self.email, self.password, self.title, 
                                 self.filename), 
            shell=True
        )


class WebdriverTorso(object):
    """
    Webdriver Torso video generation class. An abstraction to the process of
    generating and uploading a video to a given channel.
    """

    def __init__(self, *args, **kwargs):

        # We expect to feed this class directly from the commandline
        # arguments, however I prefer setting default values here so this class
        # can be potentially called fro anywhere.
        self.title_length = kwargs.get('title_length', 6)
        self.video_size = tuple(map(
            lambda x: int(x),
            kwargs.get('video_size', '854,480').split(',')
        ))
        self.slides_number = kwargs.get('slides_number', 10)
        self.folder_prefix = kwargs.get('folder_prefix', 'sm')
        self.channel_email = kwargs.get('channel_email',
                                        'yourchannel@gmail.com')
        self.password = kwargs.get('channel_password', 'yourpassword')
        self.rectangle_colors = tuple(
            [tuple(map(lambda x: int(x), color.split(','))) for color in
             kwargs.get('rectangle_colors', '21,23,27|186,4,22').split('|')]
        )
        self.background_color = tuple(map(
            lambda x: int(x),
            kwargs.get('background_color', '0,0,0').split(',')
        ))
        self.text_color = tuple(map(
            lambda x: int(x),
            kwargs.get('text_color', '255,255,255').split(',')
        ))
        self.text = kwargs.get('text', 'sky.flv - Slide {:04d}')
        self.output_file = kwargs.get('output_file', 'out.mp4')
        self.cleanup = kwargs.get('no_cleanup', True)
        self.upload = kwargs.get('no_upload', True)
        self.delay = kwargs.get('delay', 40)

    def get_name(self):
        return 'tmp' + ''.join(
            [choice(printable[:62]) for x in range(self.title_length)]
        )

    def get_folder_name(self, title):
        # A folder with the date is the most practical way to sort the videos.
        # I don't want any further details about the videos.
        today = datetime.now()
        today_code = '%s%s%s' % (today.year, today.month, today.day)
        return '%s_%s_%s' % (self.folder_prefix, today_code, title)

    def start(self, forever=False):
        """Video generation and upload process"""

        # We could do this forever (see the last lines)
        while True:
            name = self.get_name()
            makedirs(self.get_folder_name(name))
            image_generator = ImageGenerator(
                image_size=self.video_size,
                rectangle_colors=self.rectangle_colors,
                background_color=self.background_color,
                text=self.text,
                font_name='courbd.ttf',
                text_color=self.text_color
            )

            sound_generator = SoundGenerator()
            samples = []
            video_generator = VideoGenerator(
                r'slide_%04d.png', '%s.wav' % name,
                self.slides_number,
                self.output_file
            )

            uploader = VideoUploader(self.channel_email, self.password, name,
                                     self.output_file)

            for i in range(self.slides_number):
                samples.append(sound_generator.get_samples(randint(500, 2400)))
                image = image_generator.get_image(i)

                ImageGenerator.save_image(
                    image=image,
                    path='%s/slide_%04i.png' % (self.get_folder_name(name), i+1)
                )

                # We repeat the first slide in the sequence due to a bug in
                # ffmpeg where the first frame of the output video doesn't
                # respect the fps provided (it skips instantly).
                if i == 0:
                    ImageGenerator.save_image(
                        image=image,
                        path='%s/slide_0000.png' % self.get_folder_name(name)
                    )

            SoundGenerator.save_sound(
                chain(*samples),
                '%s/%s.wav' % (self.get_folder_name(name), name)
            )

            chdir(self.get_folder_name(name))
            video_generator.generate()
            if self.upload:
                uploader.upload()
            chdir('..')

            if self.cleanup:
                rmtree(self.get_folder_name(name))

            if not forever:
                # Everything comes to an end.
                break
            else:
                # Until that, we stand still...
                time.sleep(self.delay)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--title_length', required=False, type=int,
                        help='Length of video title (without including '
                             'tmp prefix)')
    parser.add_argument('-s', '--video_size', required=False,
                        help='Output video size in the format: widht,height')
    parser.add_argument('-n', '--slides_number', required=False, type=int,
                        help='Number of slides to produce')
    parser.add_argument('-f', '--folder_prefix', required=False,
                        help='Folder prefix for generated output')
    parser.add_argument('-e', '--channel_email', required=False,
                        help='YouTube channel email account')
    parser.add_argument('-p', '--channel_password', required=False,
                        help='YouTube channel password')

    # Spaces are not tolerated when parsing color arguments (nor with
    # dimentional values). I have no plans to change this myself.
    parser.add_argument('-c', '--rectangle_colors', required=False,
                        help='Rectangle colors in format: '
                             'r1,g1,b1|r2,g2,b2|r3... (as many as you want)')
    parser.add_argument('-b', '--background_color', required=False,
                        help='Background color in format: r,g,b')
    parser.add_argument('-x', '--text_color', required=False,
                        help='Text color in format: r,g,b')

    # Further details in python string formatting (using the format() str
    # function) can be seen in the official documentation.
    parser.add_argument('-t', '--text', required=False,
                        help='Text for the slides. e.g.: Slide {:04d} '
                             '(numbers are optional)')
    parser.add_argument('-o', '--output_file', required=False,
                        help='Name for the output video file.')
    parser.add_argument('--no_cleanup', action='store_false',
                        default=True, help='Do not clean the generated folders')
    parser.add_argument('--forever', action='store_true',
                        default=False, help='Generate and/or upload forever.')
    parser.add_argument('--no_upload', action='store_false', default=True,
                        help='Do not upload to YouTube')
    parser.add_argument('--sleep', required=False, type=int,
                        help='Seconds to sleep in forever mode')

    args = parser.parse_args()
    args = {k: v for k, v in args.__dict__.items() if v is not None}

    torso = WebdriverTorso(**args)
    torso.start(forever=args['forever'])