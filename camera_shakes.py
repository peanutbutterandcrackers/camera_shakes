#!/usr/bin/env python

# Subtle shake:
# Horizontal and vertical movement range [-5, 5]
# Rotation Range [-0.5, 0.5]

from gimpfu import *
import easy_easer, pytweening
import math, random

xOffsetLowerBound = -5
xOffsetUpperBound = 5
yOffsetLowerBound = -5*2
yOffsetUpperBound = 5*2

rotationLowerBound = -0.5*2
rotationUpperBound = 0.1*2

xOffsetMidPoint = (xOffsetLowerBound + xOffsetUpperBound) / 2
yOffsetMidPoint = (yOffsetUpperBound + yOffsetUpperBound) / 2
rotationMid = (rotationLowerBound + rotationUpperBound ) / 2

xOffSigma = 1.5
yOffSigma = 1.25
rotSigma  = 0.125

def camera_shake(image, drawable, total_keyframes, in_betweens):
	pdb.gimp_image_undo_group_start(image)

	shakee = pdb.gimp_image_get_active_layer(image) # the layer that will be shaked

	total_frames = (in_betweens + 1) * (total_keyframes - 1) + 1
	frames_done = 0

	pdb.gimp_message("Total Animation Frames: %s" % total_frames)

	while frames_done < total_frames:
		xOffKeyFrameA = random.gauss(xOffsetMidPoint, xOffSigma)
		yOffKeyFrameA = random.gauss(yOffsetMidPoint, yOffSigma)
		rotKeyFrameA = random.gauss(rotationMid, rotSigma)
		xOffKeyFrameB = random.gauss(xOffsetMidPoint, xOffSigma)
		yOffKeyFrameB = random.gauss(yOffsetMidPoint, yOffSigma)
		rotKeyFrameB = random.gauss(rotationMid, rotSigma)

		rem_frames = total_frames - frames_done
		steps = in_betweens + 2 # user-specified in_betweens + 2 Key Frames
		if steps > rem_frames:
			steps = rem_frames

		xOffTweens = easy_easer.MegaTweenWrapper(pytweening.linear, steps, xOffKeyFrameA, xOffKeyFrameB)
		yOffTweens = easy_easer.MegaTweenWrapper(pytweening.linear, steps, yOffKeyFrameA, yOffKeyFrameB)
		rotTweens = easy_easer.MegaTweenWrapper(pytweening.linear, steps, rotKeyFrameA, rotKeyFrameB)

		for i in range(steps):
			new_frame = pdb.gimp_layer_copy(shakee, TRUE)
			pdb.gimp_image_insert_layer(image, new_frame, None, 0)

			# offset drawable in x and y axis
			pdb.gimp_drawable_offset(new_frame, FALSE, OFFSET_TRANSPARENT, xOffTweens[i], yOffTweens[i])
			# random rotation on every single frame
			pdb.gimp_item_transform_rotate(new_frame, math.radians(rotTweens[i]), TRUE, 0, 0)

			# TODO: Merge new_frame down with previous layer, remove new_frame and set the merged_layer as the new_frame
			# This will prevent the final image sequence from having different borders, brings about uniformity and the illusion works better

			frames_done += 1
		
	pdb.gimp_image_undo_group_end(image)

register(
        "python_fu_camera_shake",
        "Camera Shake Emulation",
        "Create an image sequence that animates camera shakes",
        "Prafulla Giri", "Prafulla Giri", "2019",
        "Camera Shake...",
        "*",
        [
		(PF_IMAGE, "image", "Takes current Image", None),
		(PF_DRAWABLE, "drawable", "Input Layer", None),
		(PF_INT, "total_keyframes", "Camera Shake Keyframes", 50),
		(PF_INT, "in_betweens", "number of frames in between camera shake keyframes", 2)
        ],
        [],
        camera_shake,
        menu="<Image>/Filters/Custom"
)

main()

