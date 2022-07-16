bl_info = {
    "name": "RaC Trilogy armor_*.ps3 Model",
    "author": "Thatrandomlurker",
    "version": (0, 0, 1),
    "blender": (3, 1, 2),
    "location": "File > Import-Export",
    "description": "Import Ratchet & Clank Collection/Trilogy armor*.ps3 files",
    "warning": "",
    "doc_url": "",
    "support": 'TESTING',
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class ImportRACPS3Model(Operator, ImportHelper):
    """Import an armor from RaC Trilogy PS3 or Vita"""
    bl_idname = "ractrilogy.import_armor"
    bl_label = "Import RaC Trilogy Model"
    from . import import_armor

    filename_ext = ".ps3"

    filter_glob: StringProperty(
        default="*.ps3",
        options={'HIDDEN'}
    )

    importMode: EnumProperty(items={("VITA", "VITA", "Import from PSVITA (No Textures)"), ("PS3", "PS3", "Import from PS3")}, default="PS3", name="Platform")
    searchForSkeleton: BoolProperty(default=True, name="Search for skeleton\n(requires file to be within original folder structure)")

    def execute(self, context):
        return import_armor.ReadArmor(context, self.filepath, self.importMode, self.searchForSkeleton)
    
def menu_func_import(self, context):
    self.layout.operator(ImportRACPS3Model.bl_idname, text="Import RaC Trilogy Armor Model")

def register():
    bpy.utils.register_class(ImportRACPS3Model)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportRACPS3Model)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
