#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
"""Initialise a GUI to pick various points on images.

This Module provides a class to initialise a GUI, to pick various points
on one or multiple images.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import bb_stitcher.helpers as helpers
import bb_stitcher.picking.draggables as draggs


class PointPicker(object):
    """GUI for picking points."""

    def __init__(self):
        """Initialise GUI to pick various point on an image."""
        mpl.rcParams['keymap.quit'] = ['q', 'ctrl+w', 'cmd+w']
        mpl.rcParams['keymap.home'] = ['h', 'home']
        mpl.rcParams['keymap.zoom'] = ['z', 'o']
        mpl.rcParams['keymap.save'] = ['ctrl+s']

    def pick(self, images, all_pts=True):
        """Initialise a GUI to pick points on multiple images.

        A matplot GUI will be initialised, where the user can pick multiple points
        on the **N** ``images``. Afterwards the :obj:`PointPicker` will return **N** ndarrays, which
        holds the coordinates of the marked points. Each ndarray holds the points for one image.

        Args:
            images (list(ndarray)): List of images (ndarray)
            all_pts (bool): If ``True`` all points will be returned and else just 'selected' \
            points will be returned.

        Returns:
            list(ndarray): Returns a List of length **N**, where each cell contains a ndarray \
            *(M,2)*, which holds the coordinates of the *M* marked points per image.
        """
        imgs_a = []
        for img in images:
            imgs_a.append(helpers.add_alpha_channel(img))
        count_images = len(imgs_a)
        # creating one list per image, which will hold the draggable marks
        # e.g. for 2 images:
        # dms_per_image = [[<dragableMarks first image>],[<dragableMarks second image>]]

        dms_per_image = []
        for __ in range(count_images):
            dms_per_image.append(draggs.DraggableMarkList())

        def _on_click(event):
            # double click left mouse button
            if event.button == 1 and event.dblclick:
                for i, ax in enumerate(axes):
                    if event.inaxes == ax:
                        marker, = ax.plot(
                            event.xdata, event.ydata, 'xr', markersize=10, markeredgewidth=2)
                        dm = draggs.DraggableMark(marker, imgs_a[i])
                        dm.connect()
                        dms_per_image[i].append(dm)
                        fig.canvas.draw()

        fig, axes = plt.subplots(
            nrows=1, ncols=count_images, tight_layout=False)
        fig.canvas.mpl_connect('button_press_event', _on_click)
        fig.canvas.set_window_title('Point Picker | r-refine point | s-select point | z-zoom | '
                                    'p-pan | q-quit/finish')

        # if the nrows == 1 and ncols == 1 the function of plt.subplots returns a single
        # class 'matplotlib.axes._subplots.AxesSubplot' but we want always an array
        if count_images == 1:
            axes = np.array([axes])

        for i, image in enumerate(imgs_a):
            # don't draw y-axis on every image, just on first image
            if i > 0:
                plt.setp(axes[i].get_yticklabels(), visible=False)
            axes[i].imshow(image)

        plt.show()
        points = []
        for i, dms in enumerate(dms_per_image):
            points_per_image = dms.get_points(all_pts=all_pts)
            points.append(points_per_image)
        return points
