import arcpy

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Lab 5 Toolbox"
        self.alias = "Lab5Toolbox"
        
        # Link the tool we define below to this toolbox
        self.tools = [GarageBuildingIntersection]

class GarageBuildingIntersection(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Lab5 Toolbox"
        self.description = "Determines which buildings on TAMU's campus are near a targeted building"
        self.canRunInBackground = False
        
        # This creates the folder (Toolset) you saw in ArcGIS Pro!
        self.category = "Building Tools"

    def getParameterInfo(self):
        """Define the 6 input parameters for the tool's UI"""
        param0 = arcpy.Parameter(
            displayName="GDB Folder", name="GDBFolder", datatype="DEFolder",
            parameterType="Required", direction="Input")
            
        param1 = arcpy.Parameter(
            displayName="GDB Name", name="GDBName", datatype="GPString",
            parameterType="Required", direction="Input")
            
        param2 = arcpy.Parameter(
            displayName="Garage CSV File", name="GarageCSVFile", datatype="DEFile",
            parameterType="Required", direction="Input")
            
        param3 = arcpy.Parameter(
            displayName="Garage Layer Name", name="GarageLayerName", datatype="GPString",
            parameterType="Required", direction="Input")
            
        param4 = arcpy.Parameter(
            displayName="Campus GDB", name="CampusGDB", datatype="DEWorkspace",
            parameterType="Required", direction="Input")
            
        param5 = arcpy.Parameter(
            displayName="Buffer Distance (Meters)", name="BufferDistance", datatype="GPDouble",
            parameterType="Required", direction="Input")

        params = [param0, param1, param2, param3, param4, param5]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        """This is where the real work happens when the user clicks Run."""
        
        # Allow overwriting outputs so we can test the tool multiple times without errors
        arcpy.env.overwriteOutput = True 

        # 1. Grab the values the user typed in
        folder_path = parameters[0].valueAsText
        gdb_name = parameters[1].valueAsText
        gdb_path = folder_path + '\\' + gdb_name
        
        # 2. Create a fresh Geodatabase
        arcpy.CreateFileGDB_management(folder_path, gdb_name)

        # 3. Convert the garage CSV into a point feature layer
        csv_path = parameters[2].valueAsText
        garage_layer_name = parameters[3].valueAsText
        garages = arcpy.MakeXYEventLayer_management(csv_path, 'X', 'Y', garage_layer_name)
        
        arcpy.FeatureClassToGeodatabase_conversion(garages, gdb_path)
        garage_points = gdb_path + '\\' + garage_layer_name

        # 4. Copy the Structures layer from the Campus GDB over to our new GDB
        campus = parameters[4].valueAsText
        buildings_campus = campus + '\\Structures'
        buildings = gdb_path + '\\Buildings'
        
        arcpy.CopyFeatures_management(buildings_campus, buildings)

        # 5. Re-project the garage points to match the buildings' spatial reference
        spatial_ref = arcpy.Describe(buildings).spatialReference
        garage_reprojected = gdb_path + '\\Garage_Points_reprojected'
        arcpy.Project_management(garage_points, garage_reprojected, spatial_ref)

        # 6. Buffer the garages (automatically appending 'Meters' to the user's input)
        buffer_distance_val = parameters[5].valueAsText
        buffer_distance_str = f"{buffer_distance_val} Meters"
        garage_buffered = gdb_path + '\\Garage_Points_buffered'
        
        arcpy.Buffer_analysis(garage_reprojected, garage_buffered, buffer_distance_str)

        # 7. Intersect the buffered garages with the buildings
        intersect_output = gdb_path + '\\Garage_Buildings_Intersection'
        arcpy.Intersect_analysis([garage_buffered, buildings], intersect_output, 'ALL')

        # 8. Export the intersection results to a CSV file in the user's chosen folder
        arcpy.TableToTable_conversion(intersect_output, folder_path, 'nearbyBuildings.csv')

        return