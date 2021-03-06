from os.path import join
from tempfile import mkdtemp

from cv2 import imread
import pytest

from dvt.core import DataExtraction, FrameInput, ImageInput
from dvt.utils import setup_tensorflow
from dvt.annotate.color import ColorHistogramAnnotator, DominantColorAnnotator
from dvt.annotate.diff import DiffAnnotator
from dvt.annotate.embed import EmbedAnnotator, EmbedFrameKerasResNet50
from dvt.annotate.face import FaceAnnotator, FaceDetectMtcnn, FaceEmbedVgg2
from dvt.annotate.hofm import HOFMAnnotator
from dvt.annotate.img import ImgAnnotator
from dvt.annotate.obj import ObjectAnnotator, ObjectDetectRetinaNet
from dvt.annotate.opticalflow import OpticalFlowAnnotator
from dvt.annotate.png import PngAnnotator

from dvt.aggregate.audio import SpectrogramAggregator, PowerToneAggregator

@pytest.fixture(scope="session")
def run_setup_tensorflow():
    setup_tensorflow()


@pytest.fixture(scope="session")
def test_img():
    return imread("test-data/img/frame-000506.png")


@pytest.fixture(scope="session")
def get_video_annotation():
    setup_tensorflow()

    output_dir = mkdtemp()
    png_output = join(output_dir, "png")
    oflow_output = join(output_dir, "oflow")

    de = DataExtraction(FrameInput(
        input_path="test-data/video-clip.mp4", bsize=256
    ))

    freq = 128
    de.run_annotators([
        ColorHistogramAnnotator(freq=freq),
        DominantColorAnnotator(freq=freq),
        DiffAnnotator(quantiles=[40]),
        EmbedAnnotator(embedding=EmbedFrameKerasResNet50(), freq=freq),
        FaceAnnotator(
            detector=FaceDetectMtcnn(),
            embedding=FaceEmbedVgg2(),
            freq=freq
        ),
        HOFMAnnotator(freq=freq),
        ObjectAnnotator(detector=ObjectDetectRetinaNet(), freq=freq),
        OpticalFlowAnnotator(output_dir=oflow_output, freq=freq),
        PngAnnotator(output_dir=png_output, freq=freq)
    ], max_batch=2)

    return de, output_dir


@pytest.fixture(scope="session")
def get_video_frame_annotation():
    setup_tensorflow()

    output_dir = mkdtemp()
    png_output = join(output_dir, "png")
    oflow_output = join(output_dir, "oflow")

    de = DataExtraction(FrameInput(
        input_path="test-data/video-clip.mp4", bsize=128
    ))

    frames = [1, 3, 310]   # make sure there is an empty batch: 128-255
    de.run_annotators([
        ColorHistogramAnnotator(frames=frames, colorspace="lab"),
        DominantColorAnnotator(frames=frames),
        DiffAnnotator(quantiles=[40]),
        EmbedAnnotator(embedding=EmbedFrameKerasResNet50(), frames=frames),
        FaceAnnotator(
            detector=FaceDetectMtcnn(),
            embedding=FaceEmbedVgg2(),
            frames=frames
        ),
        HOFMAnnotator(frames=frames),
        ObjectAnnotator(detector=ObjectDetectRetinaNet(), frames=frames),
        OpticalFlowAnnotator(output_dir=oflow_output, frames=frames),
        PngAnnotator(output_dir=png_output, frames=frames),
        ImgAnnotator()
    ])

    return de, output_dir


@pytest.fixture(scope="session")
def get_image_annotation():
    setup_tensorflow()

    output_dir = mkdtemp()
    png_output = join(output_dir, "png")
    oflow_output = join(output_dir, "oflow")

    de = DataExtraction(ImageInput(
        input_paths="test-data/img/*"
    ))

    de.run_annotators([
        ColorHistogramAnnotator(colorspace="luv"),
        DominantColorAnnotator(),
        EmbedAnnotator(embedding=EmbedFrameKerasResNet50()),
        FaceAnnotator(
            detector=FaceDetectMtcnn(),
            embedding=FaceEmbedVgg2()
        ),
        ObjectAnnotator(detector=ObjectDetectRetinaNet()),
        PngAnnotator(output_dir=png_output, size=229),
        ImgAnnotator()
    ])

    return de, output_dir


@pytest.fixture(scope="session")
def get_audio_subtitle_annotation():
    setup_tensorflow()

    output_dir = mkdtemp()
    spec_output = join(output_dir, "spec")
    tone_output = join(output_dir, "tone")

    de = DataExtraction(FrameInput(
        input_path="test-data/video-clip.mp4", bsize=256
    ), ainput="test-data/video-clip.wav", sinput="test-data/video-clip.srt")

    de.run_audio_annotator()
    de.run_subtitle_annotator()

    breaks = [0, 20, 150, 200]
    de.run_aggregator(SpectrogramAnnotator(
        output_dir=spec_output, breaks=breaks
    ))
    de.run_aggregator(SpectrogramAnnotator(
        spectrogram=True, breaks=breaks, name="spec-data"
    ))
    de.run_aggregator(PowerToneAnnotator(
        output_dir=tone_output, breaks=breaks
    ))

    return de, output_dir
