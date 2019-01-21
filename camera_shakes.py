#!/usr/bin/env python

# Subtle shake:
# Horizontal and vertical movement range [-5, 5]
# Rotation Range [-0.5, 0.5]

from gimpfu import *
import easy_easer
import math, random

xOffsetLowerBound = -5
xOffsetUpperBound = 5
yOffsetLowerBound = -5
yOffsetUpperBound = 5

rotationLowerBound = -0.5
rotationUpperBound = 0.1

xOffsetMidPoint = (xOffsetLowerBound + xOffsetUpperBound) / 2
yOffsetMidPoint = (yOffsetUpperBound + yOffsetUpperBound) / 2
rotationMid = (rotationLowerBound + rotationUpperBound ) / 2

def camera_shake(image, drawable, total_frames):
	pdb.gimp_image_undo_group_start(image)

	shakee = pdb.gimp_image_get_active_layer(image) # the layer that will be shaked

	frames_done = 0
	while frames_done != total_frames: # 'less than', so as to have one extra - because randrange is [x, y) in nature
		steps = random.randrange(total_frames - frames_done) + 1 # +1 to ensure that there will never be 0

		xOffsetLow = random.randint(int(xOffsetLowerBound), int(xOffsetMidPoint))
		xOffsetHi = random.randint(int(xOffsetMidPoint), int(xOffsetUpperBound))
		yOffsetLow = random.randint(int(yOffsetLowerBound), int(yOffsetMidPoint))
		yOffsetHi = random.randint(int(yOffsetMidPoint), int(yOffsetUpperBound))
		rotLow = random.randint(int(rotationLowerBound), int(rotationMid))
		rotHi = random.randint(int(rotationMid), int(rotationUpperBound))

		xOffsetList = easy_easer.MegaTweenWrapper(random.choice(easy_easer.TweeningFunctions), steps, xOffsetLow, xOffsetHi)
		yOffsetList = easy_easer.MegaTweenWrapper(random.choice(easy_easer.TweeningFunctions), steps, yOffsetLow, yOffsetHi)
		rotationTable = easy_easer.MegaTweenWrapper(random.choice(easy_easer.TweeningFunctions), steps, rotLow, rotHi)

		if frames_done % 2 != 0:
			xOffsetList.reverse()
			yOffsetList.reverse()
			rotationTable.reverse()

		for i in range(steps):
			new_frame = pdb.gimp_layer_copy(shakee, TRUE)
			pdb.gimp_image_insert_layer(image, new_frame, None, 0)

			# offset drawable in x and y axis
			pdb.gimp_drawable_offset(new_frame, FALSE, OFFSET_TRANSPARENT, xOffsetList[i], yOffsetList[i])

			# random rotation on every single frame
			pdb.gimp_item_transform_rotate(new_frame, math.radians(rotationTable[i]), TRUE, 0, 0)
			#pdb.gimp_item_transform_rotate(new_frame, math.radians(random.random() * (rotationUpperBound - rotationLowerBound) + rotationLowerBound), TRUE, 0, 0)
			#pdb.gimp_item_transform_rotate(new_frame, math.radians(random.random() * (rotHi - rotLow) + rotLow), TRUE, 0, 0)


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
		(PF_INT, "total_frames", "Camera Shake Duration (in frames)", 77)
        ],
        [],
        camera_shake,
        menu="<Image>/Filters/Custom"
)

main()

