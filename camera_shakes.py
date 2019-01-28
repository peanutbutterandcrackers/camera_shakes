#!/usr/bin/env python

from gimpfu import *
import easy_easer, pytweening
import math, random

def camera_shake(image, drawable, total_keyframes, in_betweens, xOffsetLowerBound, xOffsetUpperBound,
  yOffsetLowerBound, yOffsetUpperBound, rotationLowerBound, rotationUpperBound, prevent_overflow, vary_offset_mean,
     xOffSigma, yOffSigma, rotSigma, seamless, link_keyframes):

	pdb.gimp_image_undo_group_start(image)

	# script behaviours
	toggle_keyframe_linking_randomly = False
	toggle_offset_mean_alteration_randomly = False

	shakee = pdb.gimp_image_get_active_layer(image) # the layer that will be shaked
	
	xOffsetMean = (xOffsetLowerBound + xOffsetUpperBound) / 2 # xOffsetMidPoint
	yOffsetMean = (yOffsetUpperBound + yOffsetUpperBound) / 2 # yOffsetMidPoint
	rotationMean = (rotationLowerBound + rotationUpperBound ) / 2 # rotationMidPoint

	total_frames = (in_betweens + 1) * (total_keyframes - 1) + 1
	frames_done = 0
	pdb.gimp_message("Total Animation Frames: %s" % total_frames)

	if link_keyframes == "Intermittently":
		toggle_keyframe_linking_randomly = True

	if vary_offset_mean == "Intermittently":
		toggle_offset_mean_alteration_randomly = True

	while frames_done < total_frames:

		if toggle_keyframe_linking_randomly:
			link_keyframes = random.choice(True, False)

		if toggle_offset_mean_alteration_randomly:
			vary_offset_mean = random.choice(True, False)

		if vary_offset_mean:
			# use random.triangular to get a mean that moves around. Yet, because
			# of triangular distribution, the offset mid points are more likely to turn up.
			xOffsetMean = random.triangular(xOffsetLowerBound, xOffsetUpperBound)
			yOffsetMean = random.triangular(yOffsetLowerBound, yOffsetUpperBound)
			rotationMean = random.triangular(yOffsetLowerBound, yOffsetUpperBound)

		# If this is the first frame and 'seamless' is false, OR if link_keyframes is false,
		# set A-frames to a random value; if link_keyframes is true, B-frame will become the
		# A-frames next time through the loop: linking every single keyframe in the sequence
		if (not link_keyframes) or (frames_done == 0 and (not seamless)):
			xOffKeyFrameA = random.gauss(xOffsetMean, xOffSigma)
			yOffKeyFrameA = random.gauss(yOffsetMean, yOffSigma)
			rotKeyFrameA = random.gauss(rotationMean, rotSigma)

		# B-frames have to be calculated, no matter what
		xOffKeyFrameB = random.gauss(xOffsetMean, xOffSigma)
		yOffKeyFrameB = random.gauss(yOffsetMean, yOffSigma)
		rotKeyFrameB = random.gauss(rotationMean, rotSigma)

		# For the first shake start interpolating the shake from 0s.
		if frames_done == 0 and seamless:
				xOffKeyFrameA, yOffKeyFrameA, rotKeyFrameA = 0, 0, 0
				# TODO: Perhaps have seamlessness be a slider and have a line akin to the following to decrease
				# B-frames in the 1st and A-frames in the last shake so as to make them even less notice-able.
				# The more the seamless-ness value, the greater the denominator. Find better mathematical expr.
				# xOffKeyFrameB, yOffKeyFrameB, rotKeyFrameB = xOffKeyFrameB/2, yOffKeyFrameB/2, rotKeyFrameB/2
				# if seamless: # Makes more sense to have B-frames defined before this one

		rem_frames = total_frames - frames_done
		steps = in_betweens + 2 # user-specified in_betweens + 2 Key Frames

		# For the last shake
		if steps >= rem_frames:
			steps = rem_frames
			if seamless:
				# Make the sequence seamless by ending up the same way as the base (untouched layer)
				# i.e. no shakes in the last layer
				xOffKeyFrameB, yOffKeyFrameB, rotKeyFrameB = 0, 0, 0

		# Prevent values from overflowing out of bounds
		if prevent_overflow:
			xOffKeyFrameA = min(xOffsetUpperBound, max(xOffsetLowerBound, xOffKeyFrameA))
			xOffKeyFrameB = min(xOffsetUpperBound, max(xOffsetLowerBound, xOffKeyFrameB))
			yOffKeyFrameA = min(yOffsetUpperBound, max(yOffsetLowerBound, yOffKeyFrameA))
			yOffKeyFrameB = min(yOffsetUpperBound, max(yOffsetLowerBound, yOffKeyFrameB))
			rotKeyFrameA = min(rotationUpperBound, max(rotationLowerBound, rotKeyFrameA))
			rotKeyFrameB = min(rotationUpperBound, max(rotationLowerBound, rotKeyFrameB))

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

		if link_keyframes:
			xOffKeyFrameA, yOffKeyFrameA, rotKeyFrameA = xOffKeyFrameB, yOffKeyFrameB, rotKeyFrameB

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
		(PF_BOOL, "prevent_overflow", "Prevent Offset Overflows", True),
		(PF_OPTION, "vary_offset_mean", "Vary Offset Mean", 1, (True, False, "Intermittently")),
		(PF_FLOAT, "xOffSigma", "X Offset Sigma", 1.5),
		(PF_FLOAT, "yOffSigma", "Y Offset Sigma", 1.25),
		(PF_FLOAT, "rotSigma", "Rotation Sigma", 0.125),
		(PF_BOOL, "seamless", "Seamless", True),
		(PF_OPTION, "link_keyframes", "Link Keyframes", 2, (True, False, "Intermittently"))
        ],
        [],
        camera_shake,
        menu="<Image>/Filters/Custom"
)

main()
