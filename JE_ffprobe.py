import ffmpeg

class JE_FFProbe():

    def __init__(self, video_path):

        self.video_path = video_path

        self.probe = ffmpeg.probe(video_path)
        self.format = self.probe["format"]
        self.streams = self.probe["streams"]

    def get_stream_codes(self):

        return [s["codec_tag_string"] for s in self.streams]

    def log_dict_sumary(self, log_dict, prefix=""):

        for k, v in log_dict.items():
            if type(v) is list:
                print(prefix, k, "- list")
                self.log_dict_sumary(v[0], prefix + "  ")
            elif type(v) is dict:
                print(prefix, k, "- dict")
                self.log_dict_sumary(v, prefix + "  ")
            else:
                print(prefix, k, "-", v)

    def log(self):

        print("")
        print("JE_FFProbe do_print() - ", self.video_path)
        print("=====================")
        self.log_dict_sumary(self.format)
        print("STREAMS:", self.get_stream_codes())
        for s in self.streams:
            print("STREAM: ", s["codec_tag_string"])
            self.log_dict_sumary(s)

    def extract_bin_stream(self, codec_tag, verbose=False):

        stream_index = -1
        for s in self.streams:
            if s["codec_tag_string"] == codec_tag:
                stream_index = s["index"]

        assert stream_index != -1, f"codec_tag {codec_tag} not found in {self.video_path10}"

        ffmpeg_input = ffmpeg.input(self.video_path)
        ffmpeg_output = ffmpeg_input.output("pipe:", format="rawvideo", map="0:%i" % stream_index, codec="copy")
        bin = ffmpeg_output.run(capture_stdout=True, capture_stderr=not verbose)

        return bin[0]
