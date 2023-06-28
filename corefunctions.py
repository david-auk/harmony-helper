import essentia.standard as es

circleOfFithsResolver = {
    'C': 'Am',
    'Am': 'C',

    'G': 'Em',
    'Em': 'G',

    'D': 'Bm',
    'Bm': 'D',

    'A': 'F#m',
    'F#m': 'A',

    'E': 'C#m',
    'C#m': 'E',

    'B': 'G#m',
    'G#m': 'B',

    'F#': 'D#m',
    'D#m': 'F#',

    'C#': 'A#m',
    'A#m': 'C#',

    'G#': 'Fm',
    'Fm': 'G#',

    'D#': 'Cm',
    'Cm': 'D#',

    'A#': 'Gm',
    'Gm': 'A#',

    'F': 'Dm',
    'Dm': 'F'
}

keyPosition = {
    'C': 1,
    'C#': 2,
    'D': 3,
    'D#': 4,
    'E': 5,
    'F': 6,
    'F#': 7,
    'G': 8,
    'G#': 9,
    'A': 10,
    'A#': 11,
    'B': 12
}

def analyzeSongKey(audio_path):
    loader = es.MonoLoader(filename=audio_path)
    audio = loader()

    key_extractor = es.KeyExtractor()
    key, scale, confidence = key_extractor(audio)

    return key, scale

def circleOfFithResolver(key, keyType):
    if keyType == 'minor':
        fifthResolved = circleOfFithsResolver[f"{key}m"]
        key = fifthResolved
        keyType = 'majeur'
    else:
        fifthResolved = circleOfFithsResolver[key]
        key = fifthResolved.replace('m', '')
        keyType = 'minor'

    return (key, keyType)

def distanceCalc(instrumentalKey, vocalKey): # This only works (music theoreticly correct) if the two diffrent tracks are the same type. this function is not responsible for correcting types

    instrumentalKeyPos = keyPosition[instrumentalKey]
    vocalKeyPos = keyPosition[vocalKey]

    if vocalKeyPos == instrumentalKeyPos:
        shortestSemitoneDistance = 0 # The Two are the exact same
    

    elif vocalKeyPos > instrumentalKeyPos:
        
        # Vocal is greater (higher) then beat

        semitoneDistanceDown = vocalKeyPos - instrumentalKeyPos # The downwards distance (Same octave because the vocal is already the higest in the octave) between the Vocal to the Beat
        semitoneDistanceUp = instrumentalKeyPos + 12 - vocalKeyPos # The upwards distance (higher octave because the vocal is already the higest in the octave) between the Vocal to the Beat

        if semitoneDistanceDown < semitoneDistanceUp:
            shortestSemitoneDistance = semitoneDistanceDown # f"Beat ({track['beat']['key']}) + {semitoneDistanceDown} Semitones = Vocal ({track['vocal']['key']}) (+{semitoneDistanceDown}00 cent)\nVocal ({track['vocal']['key']}) - {semitoneDistanceDown} Semitones = Beat ({track['beat']['key']}) (-{semitoneDistanceDown}00 cent)"
        else:
            shortestSemitoneDistance = -semitoneDistanceUp # f"Beat ({track['beat']['key']}) - {semitoneDistanceUp} Semitones = Vocal ({track['vocal']['key']}) (-{semitoneDistanceDown}00 cent)\nVocal ({track['vocal']['key']}) + {semitoneDistanceUp} Semitones = Beat ({track['beat']['key']}) (+{semitoneDistanceDown}00 cent)"

    elif vocalKeyPos < instrumentalKeyPos:
        
        # Beat is greater (higher) then Vocal
        
        semitoneDistanceDown = instrumentalKeyPos - vocalKeyPos
        semitoneDistanceUp = vocalKeyPos + 12 - instrumentalKeyPos

        if semitoneDistanceDown < semitoneDistanceUp:
            shortestSemitoneDistance = -semitoneDistanceDown #f"Beat ({track['beat']['key']}) - {semitoneDistanceDown} Semitones = Vocal ({track['vocal']['key']}) (-{semitoneDistanceDown}00 cent)\nVocal ({track['vocal']['key']}) + {semitoneDistanceDown} Semitones = Beat ({track['beat']['key']}) (+{semitoneDistanceDown}00 cent)"
        else:
            shortestSemitoneDistance = semitoneDistanceUp #f"Beat ({track['beat']['key']}) + {semitoneDistanceUp} Semitones = Vocal ({track['vocal']['key']}) (+{semitoneDistanceDown}00 cent)\nVocal ({track['vocal']['key']}) - {semitoneDistanceUp} Semitones = Beat ({track['beat']['key']}) (-{semitoneDistanceDown}00 cent)"

    return shortestSemitoneDistance

#def vocalInstrumentalHarmonisation(vocalKey, vocalKeyType, instrumentalKey, instrumentalKeyType):
#    pass