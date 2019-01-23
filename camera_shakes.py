#!/usr/bin/env python

# Subtle shake:
# Horizontal and vertical movement range [-5, 5]
# Rotation Range [-0.5, 0.5]

from gimpfu import *
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

xOffSigma = 1 
yOffSigma = 1 
rotSigma  = 1 

def camera_shake(image, drawable, total_frames):
	pdb.gimp_image_undo_group_start(image)

	shakee = pdb.gimp_image_get_active_layer(image) # the layer that will be shaked

	frames_done = 0
	while frames_done != total_frames:

		xOffsetLow = random.triangular(int(xOffsetLowerBound), int(xOffsetMidPoint))
		xOffsetHi = random.triangular(int(xOffsetMidPoint), int(xOffsetUpperBound))
		yOffsetLow = random.triangular(int(yOffsetLowerBound), int(yOffsetMidPoint))
		yOffsetHi = random.triangular(int(yOffsetMidPoint), int(yOffsetUpperBound))
		rotLow = random.triangular(int(rotationLowerBound), int(rotationMid))
		rotHi = random.triangular(int(rotationMid), int(rotationUpperBound))

		new_frame = pdb.gimp_layer_copy(shakee, TRUE)
		pdb.gimp_image_insert_layer(image, new_frame, None, 0)

		# offset drawable in x and y axis
		pdb.gimp_drawable_offset(new_frame, FALSE, OFFSET_TRANSPARENT, random.gauss(xOffsetMidPoint, xOffSigma), random.gauss(yOffsetMidPoint, yOffSigma))
		# random rotation on every single frame
		pdb.gimp_item_transform_rotate(new_frame, math.radians(random.gauss(rotationMid, rotSigma)), TRUE, 0, 0)


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

