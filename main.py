import corefunctions
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('Media', type=str, help='the Source that will get Downloaded/Processed (YouTube links | Audio files)')

args = parser.parse_args()
audio_path = args.Media

print(f'Analyzing \'{audio_path}\'')
songKey, songKeyType = corefunctions.analyzeSongKey(audio_path)

if songKey is not None:
	print(f'The key of the song is:', songKey, songKeyType)