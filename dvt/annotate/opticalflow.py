# -*- coding: utf-8 -*-
"""Annotator to extract dense Optical Flow using the opencv
Gunnar Farneback’s algorithm.
"""

import os

import numpy as np
import cv2

from ..core import FrameAnnotator
from ..utils import _proc_frame_list, _which_frames, _check_out_dir


class OpticalFlowAnnotator(FrameAnnotator):
    """Annotator to extract dense Optical Flow using the opencv Gunnar
    Farneback’s algorithm.

    The annotator will return an image or flow field describing the motion in
    two subsequent frames.

    Attributes:
        freq (int): How often to perform the embedding. For example, setting
            the frequency to 2 will computer every other frame in the batch.
        raw (bool): Return optical flow as color image by default, raw returns
            the raw output as produced by the opencv algorithm.
        frames (array of ints): An optional list of frames to process. This
            should be a list of integers or a 1D numpy array of integers. If
            set to something other than None, the freq input is ignored.
        output_dir (string): optional location to store the computed images.
            Only used if raw is set to False.
    """

    name = "opticalflow"

    def __init__(self, **kwargs):
        self.freq = kwargs.get("freq", 1)
        self.raw = kwargs.get("raw", False)
        self.frames = _proc_frame_list(kwargs.get("frames", None))
        self.output_dir = _check_out_dir(kwargs.get("output_dir", None))

    def annotate(self, batch):
        """Annotate the batch of frames with the optical flow annotator.

        Args:
            batch (FrameBatch): A batch of images to annotate.

        Returns:
            A list of dictionaries containing the video name, frame, and the
            optical flow representation. The latter has the same spatial
            dimensions as the input.
        """
        # determine which frames to work on
        frames = _which_frames(batch, self.freq, self.frames)
        frame_names = np.array(batch.get_frame_names())
        if not frames:
            return None

        # run the optical flow analysis on each frame
        flow = []
        for fnum in frames:
            flow += [_get_optical_flow(batch, fnum)]

            if not self.raw:
                flow[-1] = _flow_to_color(flow[-1])
                if self.output_dir is not None:
                    opath = os.path.join(
                        self.output_dir,
                        "frame-{0:06d}.png".format(frame_names[fnum]),
                    )
                    cv2.imwrite(filename=opath, img=flow[-1])

        obj = {"opticalflow": np.stack(flow)}

        # Add video and frame metadata
        obj["frame"] = frame_names[list(frames)]

        return obj


def _get_optical_flow(batch, fnum):

    current_gray = cv2.cvtColor(
        batch.img[fnum, :, :, :], cv2.COLOR_RGB2GRAY
    )
    next_gray = cv2.cvtColor(
        batch.img[fnum + 1, :, :, :], cv2.COLOR_RGB2GRAY
    )

    return cv2.calcOpticalFlowFarneback(
        current_gray,
        next_gray,
        flow=None,
        pyr_scale=0.5,
        levels=1,
        winsize=15,
        iterations=2,
        poly_n=5,
        poly_sigma=1.1,
        flags=0,
    )


# Optical flow to color image conversion code adapted from:
# https://github.com/tomrunia/OpticalFlow_Visualization


def _make_colorwheel():
    """
    Generates a color wheel for optical flow visualization as presented in:
        Baker et al. "A Database and Evaluation Methodology for Optical Flow"
        (ICCV, 2007) URL: http://vision.middlebury_col.edu/flow/flowEval-iccv07.pdf
    According to the C++ source code of Daniel Scharstein
    According to the Matlab source code of Deqing Sun
    """

    ry_col = 15
    yg_col = 6
    gc_col = 4
    cb_col = 11
    bm_col = 13
    mr_col = 6

    ncols = ry_col + yg_col + gc_col + cb_col + bm_col + mr_col
    colorwheel = np.zeros((ncols, 3))
    col = 0

    # ry_col
    colorwheel[0:ry_col, 0] = 255
    colorwheel[0:ry_col, 1] = np.floor(255 * np.arange(0, ry_col) / ry_col)
    col = col + ry_col
    # yg_col
    colorwheel[col:col + yg_col, 0] = 255 - np.floor(255 * np.arange(0, yg_col) / yg_col)
    colorwheel[col:col + yg_col, 1] = 255
    col = col + yg_col
    # gc_col
    colorwheel[col:col + gc_col, 1] = 255
    colorwheel[col:col + gc_col, 2] = np.floor(255 * np.arange(0, gc_col) / gc_col)
    col = col + gc_col
    # cb_col
    colorwheel[col:col + cb_col, 1] = 255 - np.floor(255 * np.arange(cb_col) / cb_col)
    colorwheel[col:col + cb_col, 2] = 255
    col = col + cb_col
    # bm_col
    colorwheel[col:col + bm_col, 2] = 255
    colorwheel[col:col + bm_col, 0] = np.floor(255 * np.arange(0, bm_col) / bm_col)
    col = col + bm_col
    # mr_col
    colorwheel[col:col + mr_col, 2] = 255 - np.floor(255 * np.arange(mr_col) / mr_col)
    colorwheel[col:col + mr_col, 0] = 255
    return colorwheel


def _flow_compute_color(hflow, vflow):
    """
    Applies the flow color wheel to (possibly clipped) flow components u and v.
    According to the C++ source code of Daniel Scharstein
    According to the Matlab source code of Deqing Sun

    Attributes:
        u (np.ndarray): horizontal flow.
        v (np.ndarray): vertical flow.
    """

    flow_image = np.zeros((hflow.shape[0], hflow.shape[1], 3), np.uint8)

    colorwheel = _make_colorwheel()  # shape [55x3]
    ncols = colorwheel.shape[0]

    rad = np.sqrt(np.square(hflow) + np.square(vflow))
    atan = np.arctan2(-vflow, -hflow) / np.pi

    fka = (atan + 1) / 2 * (ncols - 1)
    k0a = np.floor(fka).astype(np.int32)
    k1a = k0a + 1
    k1a[k1a == ncols] = 0
    faa = fka - k0a

    for i in range(colorwheel.shape[1]):

        tmp = colorwheel[:, i]
        col0 = tmp[k0a] / 255.0
        col1 = tmp[k1a] / 255.0
        col = (1 - faa) * col0 + faa * col1

        idx = rad <= 1
        col[idx] = 1 - rad[idx] * (1 - col[idx])
        col[~idx] = col[~idx] * 0.75  # out of range?

        flow_image[:, :, i] = np.floor(255 * col)

    return flow_image


def _flow_to_color(flow_uv):
    """
    Expects a two dimensional flow image of shape [H,W,2]
    According to the C++ source code of Daniel Scharstein
    According to the Matlab source code of Deqing Sun

    Attributes:
        flow_uv (np.ndarray): np.ndarray of optical flow with shape [H,W,2]
    """

    assert flow_uv.ndim == 3, "input flow must have three dimensions"
    assert flow_uv.shape[2] == 2, "input flow must have shape [H,W,2]"

    flow_u = flow_uv[:, :, 0]
    flow_v = flow_uv[:, :, 1]

    rad = np.sqrt(np.square(flow_u) + np.square(flow_v))
    rad_max = np.max(rad)

    epsilon = 1e-5
    flow_u = flow_u / (rad_max + epsilon)
    flow_v = flow_v / (rad_max + epsilon)

    return _flow_compute_color(flow_u, flow_v)
