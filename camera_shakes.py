#!/usr/bin/env python

# TODO: Instead ofthe current way of processing the image, where we enter a while loop and stuff,
# encapsulate the main effect application into a function and have a variable 'passes' that will
# determine how many passes the effect application will be done in. Even better, have each aspect
# of the effect have it's own unique 'n' number of passes.

# Subtle shake:
# Horizontal and vertical movement range [-5, 5]
# Rotation Range [-0.5, 0.5]

from gimpfu import *
import easy_easer
import math, random

import time
random.seed(time.time() * 10e10)
#random.seed(143)

xOffsetLowerBound = -5
xOffsetUpperBound = 5
yOffsetLowerBound = -5
yOffsetUpperBound = 5

rotationLowerBound = -0.5
rotationUpperBound = 0.1

def camera_shake(image, drawable, total_frames):
	pdb.gimp_image_undo_group_start(image)

	shakee = pdb.gimp_image_get_active_layer(image) # the layer that will be shaked

	easer = random.choice(easy_easer.TweeningFunctions)

	steps = total_frames / 4 # in 4 passes?
	xOffsetList = easy_easer.MegaTweenWrapper(easer, steps, xOffsetLowerBound, xOffsetUpperBound)
	yOffsetList = easy_easer.MegaTweenWrapper(easer, steps, yOffsetLowerBound, yOffsetUpperBound)
	rotationTable = easy_easer.MegaTweenWrapper(easer, steps, rotationLowerBound, rotationUpperBound)

	frames_done = 0
	while frames_done < total_frames: # 'less than', so as to have one extra - because randrange is [x, y) in nature
		#steps = random.randrange(total_frames - frames_done) + 1 # +1 to ensure that there will never be 0
		#steps = (total_frames - frames_done) / (random.randrange(total_frames - frames_done) + 1)
		#steps = (total_frames - frames_done) / random.randint(1, 4) # random integer between 1 to 4

		if frames_done % 2 != 0:
			xOffsetList.reverse()
			rotationTable.reverse()
			yOffsetList.reverse()
	#	else:

		print("Frame:", frames_done + 1, "Steps:", steps, xOffsetList, yOffsetList, rotationTable)

		for i in range(steps):
			new_frame = pdb.gimp_layer_copy(shakee, TRUE)
			pdb.gimp_image_insert_layer(image, new_frame, None, 0)

			# offset drawable in x and y axis
			pdb.gimp_drawable_offset(new_frame, FALSE, OFFSET_TRANSPARENT, xOffsetList[i], yOffsetList[i])
			# random rotation on every single frame
			pdb.gimp_item_transform_rotate(new_frame, math.radians(rotationTable[i]), TRUE, 0, 0)
			#pdb.gimp_item_transform_rotate(new_frame, math.radians(random.random() * (rotationUpperBound - rotationLowerBound) + rotationLowerBound), TRUE, 0, 0)
			# TODO: Merge new_frame down with previous layer, remove new_frame and set the merged_layer as the new_frame
			# This will prevent the final image sequence from having different borders, brings about uniformity and the illusion works better

			frames_done += 1
			if frames_done == total_frames:
				break
		
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
		(PF_INT, "total_frames", "Camera Shake Duration (in frames)", 77)
        ],
        [],
        camera_shake,
        menu="<Image>/Filters/Custom"
)

main()

