import os

import cv2
import numpy as np
import numpy.testing as npt
import pytest

import bb_stitcher.helpers as helpers
import bb_stitcher.preparation as prep
import bb_stitcher.stitcher as stitcher


@pytest.fixture
def super_stitcher():
    st = stitcher.Stitcher()
    return st


@pytest.fixture
def fb_stitcher(config):
    fbs = stitcher.FeatureBasedStitcher(config)
    return fbs


@pytest.fixture
def left_img_prep(left_img, config):
    left_img_alpha = helpers.add_alpha_channel(left_img['img'])
    rectificator = prep.Rectificator(config)
    rect_img = rectificator.rectify_image(left_img_alpha)
    rect_detections = rectificator.rectify_points(left_img['detections'], left_img['size'])

    angle = 90
    rot_img, rot_mat = prep.rotate_image(rect_img, angle)
    rot_detections = prep.rotate_points(rect_detections, angle, left_img['size'])

    d = dict()
    d['img'] = rot_img
    d['detections'] = rot_detections

    return d


@pytest.fixture
def right_img_prep(right_img, config):
    right_img_alpha = helpers.add_alpha_channel(right_img['img'])
    rectificator = prep.Rectificator(config)
    rect_img = rectificator.rectify_image(right_img_alpha)
    rect_detections = rectificator.rectify_points(right_img['detections'], right_img['size'])

    angle = -90
    rot_img, rot_mat = prep.rotate_image(rect_img, angle)
    rot_detections = prep.rotate_points(rect_detections, angle, right_img['size'])

    d = dict()
    d['img'] = rot_img
    d['detections'] = rot_detections

    return d


@pytest.fixture
def homo_left():
    homo = np.float64([
        [1, 0, 0],
        [0, 1, 199.91238403],
        [0, 0, 1]
    ])
    return homo


@pytest.fixture
def homo_right():
    homo = np.float64([
        [1.01332402e+00, 4.11682445e-02, 2.46059578e+03],
        [-4.11682445e-02, 1.01332402e+00, 1.23504729e+02],
        [0, 0, 1]
    ])
    return homo


@pytest.fixture
def pano_size():
    return (5666, 4200)


def test_super_estimate_transform(super_stitcher):
    with pytest.raises(NotImplementedError):
        super_stitcher.estimate_transform()


def test_calc_feature_mask():
    target_mask_left = np.array(
        [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0],
         [0, 255, 255],
         [0, 255, 255],
         [0, 255, 255],
         [0, 255, 255],
         [0, 0, 0],
         ], np.uint8)
    target_mask_right = np.array(
        [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0],
         [255, 255, 0],
         [255, 255, 0],
         [255, 255, 0],
         [255, 255, 0],
         [0, 0, 0],
         ], np.uint8)
    mask_left, mask_right = stitcher.FeatureBasedStitcher._calc_feature_mask(
        (3, 8), (3, 8), 2, 3, 1)
    npt.assert_equal(mask_left, target_mask_left)
    npt.assert_equal(mask_right, target_mask_right)


def test_estimate_transform(fb_stitcher, left_img_prep, right_img_prep, not_to_bee):
    # find transformation
    assert fb_stitcher.estimate_transform(left_img_prep['img'], right_img_prep['img']) is not None

    # provoke no finding of transformation
    assert fb_stitcher.estimate_transform(left_img_prep['img'], not_to_bee) is None


def test_compose_panorama(left_img_prep, right_img_prep, homo_left, homo_right, pano_size, outdir):
    st = stitcher.Stitcher(homo_left, homo_right, pano_size)
    pano = st.compose_panorama(left_img_prep['img'], right_img_prep['img'])
    out = os.path.join(outdir, 'panorama.jpg')
    cv2.imwrite(out, pano)
