import essentia.standard as es

def analyzeSongKey(audio_path):
    loader = es.MonoLoader(filename=audio_path)
    audio = loader()

    key_extractor = es.KeyExtractor()
    key, scale, confidence = key_extractor(audio)
    print(key_extractor(audio))

    return key, scale, confidence