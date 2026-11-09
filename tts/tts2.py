import sherpa_onnx
import soundfile as sf

config = sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model="vits-piper-zh_CN-xiao_ya-medium/zh_CN-xiao_ya-medium.onnx",
            lexicon="vits-piper-zh_CN-xiao_ya-medium/lexicon.txt",
            tokens="vits-piper-zh_CN-xiao_ya-medium/tokens.txt",
        ),
        num_threads=1,
    ),
    rule_fsts="vits-piper-zh_CN-xiao_ya-medium/phone.fst,vits-piper-zh_CN-xiao_ya-medium/date.fst,vits-piper-zh_CN-xiao_ya-medium/number.fst",
)

if not config.validate():
    raise ValueError("Please check your config")

tts = sherpa_onnx.OfflineTts(config)
audio = tts.generate(text="某某银行的副行长和一些行政领导表示，他们去过长江和长白山; 经济不断增长。2024年12月31号，拨打110或者18920240511。123456块钱。当夜幕降临，星光点点，伴随着微风拂面，我在静谧中感受着时光的流转，思念如涟漪荡漾，梦境如画卷展开，我与自然融为一体，沉静在这片宁静的美丽之中，感受着生命的奇迹与温柔.",
                     sid=0,
                     speed=1.0)

sf.write("test.wav", audio.samples, samplerate=audio.sample_rate)
print(audio.sample_rate)
