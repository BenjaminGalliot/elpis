from kaldi.interface import KaldiInterface


kaldi = KaldiInterface()

ds = kaldi.new_dataset('dsy')
# ds.add('/elpis/abui_toy_corpus/data/1_1_5.eaf', '/elpis/abui_toy_corpus/data/1_1_5.wav')
with open('/elpis/abui_toy_corpus/data/1_1_4.eaf', 'rb') as feaf, open('/elpis/abui_toy_corpus/data/1_1_4.wav', 'rb') as fwav:
    ds.add_fp(feaf, 'f.eaf')
    ds.add_fp(fwav, 'f.wav')
ds.process()

def transcribe():
    t = kaldi.new_transcription('tx')
    t.link(m)
    t.transcribe_align('/elpis/abui_toy_corpus/data/1_1_1.wav')
    print(t.elan().decode('utf-8'))

m = kaldi.new_model('mx')
m.link(ds)
m.set_l2s_path('/elpis/abui_toy_corpus/config/letter_to_sound.txt')
m.generate_lexicon()
m.train(on_complete=transcribe)
