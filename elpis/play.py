from kaldi.interface import KaldiInterface

kaldi = KaldiInterface()
print(kaldi.path)

ds = kaldi.new_dataset('dsx')
ds.add('/elpis/abui_toy_corpus/data/1_1_5.eaf', '/elpis/abui_toy_corpus/data/1_1_5.wav')
with open('/elpis/abui_toy_corpus/data/1_1_4.eaf', 'rb') as feaf:
    with open('/elpis/abui_toy_corpus/data/1_1_4.wav', 'rb') as fwav:
        ds.add_fp(feaf, fwav, 'f.eaf', 'f.wav')
ds.process()

m = kaldi.new_model('mx')
m.link(ds)
m.set_pronunciation_path('/elpis/abui_toy_corpus/config/letter_to_sound.txt')
m.train()

t = kaldi.new_transcription('tx', m)
# t.transcribe('/elpis/abui_toy_corpus/data/1_1_1.wav')
t.transcribe_align('/elpis/abui_toy_corpus/data/1_1_1.wav')
print(t.elan().decode('utf-8'))

# from kaldi.fsobject import FSObject

# obj = FSObject('/tmp/this')
# h = obj.hash
# obj.config['test'] = []
# obj.config['test'] += [5]
# print(obj.config)
# print("h:", h)
# print("int(h, 16):", int(h, 16))
# d = int(h, 16)
# print("hex(d):", hex(d))