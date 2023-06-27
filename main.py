import corefunctions
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--instrumental', type=str, help='Give a instrumental')
parser.add_argument('-V', '--vocal', type=str, help='Give a Vocal')

args = parser.parse_args()
instrumentalPath = args.instrumental
vocalPath = args.vocal

print('\n')

print(f'Analyzing instrumental: \'{instrumentalPath.split("/")[-1]}\'')
instrumentalKey, instrumentalKeyType = corefunctions.analyzeSongKey(instrumentalPath)

if instrumentalKey is None:
	quit()

print(f'The key of the instrumental is:', instrumentalKey, instrumentalKeyType)

print()

print(f'Analyzing vocal: \'{vocalPath.split("/")[-1]}\'')
vocalKey, vocalKeyType = corefunctions.analyzeSongKey(vocalPath)

if instrumentalKey is None:
	quit()

print(f'The key of the vocal is:', vocalKey, vocalKeyType)

print()

if instrumentalKeyType != vocalKeyType:

	print(f'Minor and Major do not harmonise. resolving Instrumental: {instrumentalKey} {instrumentalKeyType}')

	instrumentalKey, instrumentalKeyType = corefunctions.circleOfFithResolver(key=instrumentalKey, keyType=instrumentalKeyType)

	print(f'The key of the instrumental is:', instrumentalKey, instrumentalKeyType)

print('\n')

shortestSemitoneDistance = corefunctions.distanceCalc(instrumentalKey=instrumentalKey, vocalKey=vocalKey)

print(f'your instrumental instructions are: {shortestSemitoneDistance} steps (semitones), {shortestSemitoneDistance}00 cent in pitch')

