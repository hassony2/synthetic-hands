root = "/home/local2/yhasson/first-person-action-recognition/"
data_folder = root + "data/"

export_folder = data_folder + "blender-renders/"
asset_folder = data_folder + "blender-assets/"

image_folder = export_folder + "images/"
annot_folder = export_folder + "annots/"
# Blender assets folders
scene_folder = asset_folder + "scene/"
background_folder = asset_folder + "backgrounds/"


# Rendered data folderes
rgb_folder = annot_folder + "rgb/"
depth_folder = annot_folder + "depth/"

# Annotation data folders
coord_2d_folder = annot_folder + "2Dcoord/"
coord_3d_folder = annot_folder + "3Dcoord/"
segm_folder = annot_folder + "segm/"

params = {}
params["data_folder"] = data_folder
params["script_folder"] = root
params["asset_folder"] = asset_folder
params["export_folder"] = export_folder

params["image_folder"] = image_folder
params["annot_folder"] = annot_folder

params["coord_2d_folder"] = coord_2d_folder
params["coord_3d_folder"] = coord_3d_folder
params["segm_folder"] = segm_folder

params["depth_folder"] = depth_folder
params["rgb_folder"] = rgb_folder

params["background_folder"] = background_folder
params["scene_folder"] = scene_folder
