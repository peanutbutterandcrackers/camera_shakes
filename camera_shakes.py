#!/usr/bin/env python

from gimpfu import *
import easy_easer, pytweening
import math, random

def camera_shake(image, drawable, total_keyframes, in_betweens, xOffsetLowerBound, xOffsetUpperBound,
  yOffsetLowerBound, yOffsetUpperBound, rotationLowerBound, rotationUpperBound, xOffSigma,
    yOffSigma, rotSigma, seamless):
	pdb.gimp_image_undo_group_start(image)

	shakee = pdb.gimp_image_get_active_layer(image) # the layer that will be shaked
	
	xOffsetMidPoint = (xOffsetLowerBound + xOffsetUpperBound) / 2
	yOffsetMidPoint = (yOffsetUpperBound + yOffsetUpperBound) / 2
	rotationMid = (rotationLowerBound + rotationUpperBound ) / 2

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

		# For the first shake
		if frames_done == 0 and seamless:
			# start interpolating the shake from 0s.
			xOffKeyFrameA, yOffKeyFrameA, rotKeyFrameA = 0, 0, 0
			# TODO: Perhaps have seamlessness be a slider and have a line akin to the following to decrease
			# B-frames in the 1st and A-frames in the last shake so as to make them even less notice-able.
			# The more the seamless-ness value, the greater the denominator. Find better mathematical expr.
			# xOffKeyFrameB, yOffKeyFrameB, rotKeyFrameB = xOffKeyFrameB/2, yOffKeyFrameB/2, rotKeyFrameB/2

		rem_frames = total_frames - frames_done
		steps = in_betweens + 2 # user-specified in_betweens + 2 Key Frames

		# For the last shake
		if steps >= rem_frames:
			steps = rem_frames
			if seamless:
				# Make the sequence seamless by ending up the same way as the base (untouched layer)
				# i.e. no shakes in the last layer
				xOffKeyFrameB, yOffKeyFrameB, rotKeyFrameB = 0, 0, 0

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
		(PF_INT, "in_betweens", "Keyframe Inbetweens", 2),
		(PF_FLOAT, "xOffsetLowerBound", "X-Offset Lower Bound", -5),
		(PF_FLOAT, "xOffsetUpperBound", "X-Offset Upper Bound", 5),
		(PF_FLOAT, "yOffsetLowerBound", "Y-Offset Lower Bound", -5*2),
		(PF_FLOAT, "yOffsetUpperBound", "Y-Offset Upper Bound", 5*2),
		(PF_FLOAT, "rotationLowerBound", "Rotation Lower Bound", -0.5*2),
		(PF_FLOAT, "rotationUpperBound", "Rotation Upper Bound", 0.1*2),
		(PF_FLOAT, "xOffSigma", "X Offset Sigma", 1.5),
		(PF_FLOAT, "yOffSigma", "Y Offset Sigma", 1.25),
		(PF_FLOAT, "rotSigma", "Rotation Sigma", 0.125),
		(PF_BOOL, "seamless", "Seamless", True)
        ],
        [],
        camera_shake,
        menu="<Image>/Filters/Custom"
)

main()

