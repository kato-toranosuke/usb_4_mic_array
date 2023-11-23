import pyaudio
# from mic_array import MicArray
import numpy as np
import wave
import os


class MicArray:
    def __init__(self, dev_idx, out_dir_path='./out/', fs=48000, n_ch=6, chunk=1024, width=2) -> None:
        self.__dev_idx = dev_idx
        self.__out_dir_path = out_dir_path
        self.__fs = fs
        # change base on firmwares, 1_channel_firmware.bin as 1 or 6_channels_firmware.bin as 6
        self.__n_ch = n_ch
        self.__chunk = chunk
        self.__width = width

        # 出力ディレクトリを作成する
        os.makedirs(self.__out_dir_path, exist_ok=True)

    @property
    def fs(self):
        return self.__fs

    @property
    def chunk(self):
        return self.__chunk

    @property
    def out_dir_path(self):
        return self.__out_dir_path

    def record(self, sec_duration=2, fname=None) -> None:
        p = pyaudio.PyAudio()

        stream = p.open(
            rate=self.__fs,
            format=p.get_format_from_width(self.__width),
            channels=self.__n_ch,
            input=True,
            input_device_index=self.__dev_idx,)

        n_block_iter = int(self.__fs / self.__chunk * sec_duration)
        # frames = np.zeros((n_block_iter*self.__chunk*self.__width,
        #                   self.__n_ch), dtype=np.byte)
        # frames = [[] for i in range(self.__n_ch)]
        frames = []
        print(f"[Device ID:{self.__dev_idx}] * recording")

        for i in range(0, n_block_iter):
            data = stream.read(self.__chunk)

            # channelごとのデータを取得
            # for j in range(self.__n_ch):
            #     # extract channel 0 data from 6 channels, if you want to extract channel 1, please change to [1::6]
            #     data_ch = np.frombuffer(data, dtype=np.int16)[j::self.__n_ch]
            #     # frames[self.__chunk*self.__width*i:self.__chunk*self.__width*(i+1), j] = data_ch.tobytes()
            #     frames[j].append(data_ch.tobytes())

            # 全チャンネルデータを格納
            frames.append(data)

        print(f"[Device ID:{self.__dev_idx}] * done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        if fname == None:
            fname = f"dev-{self.__dev_idx}_nch-{self.__n_ch}"
        fpath = self.__out_dir_path + fname + '.wav'
        with wave.open(fpath, 'wb') as wf:
            wf.setnchannels(self.__n_ch)
            wf.setsampwidth(p.get_sample_size(
                p.get_format_from_width(self.__width)))
            wf.setframerate(self.__fs)
            wf.writeframes(b''.join(frames))
