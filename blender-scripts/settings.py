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
folders = {}
params["folders"] = folders

folders["data"] = data_folder
folders["scrip"] = root
folders["asset"] = asset_folder
folders["export"] = export_folder

folders["image"] = image_folder
folders["annot"] = annot_folder

folders["coord_2d"] = coord_2d_folder
folders["coord_3d"] = coord_3d_folder
folders["segm"] = segm_folder

folders["depth"] = depth_folder
folders["rgb"] = rgb_folder

folders["background"] = background_folder
folders["scene"] = scene_folder
