##Lab 6 with AI help add import time and valueList
import arcpy
import time # [FIX 1] Imported the time module to support time.sleep()

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Map Generation Toolbox"
        self.alias = "MapGen"
        # list of tool classes associated with this toolbox
        self.tools = [MapGenerator] # Renamed the tool class to reflect it does both map types


class MapGenerator(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Generate Thematic Map"
        self.description = "Create a graduated colored map or unique value map based on a specific attribute of a layer"
        self.canRunInBackground = False
        self.category = "MapTools"

    def getParameterInfo(self):
        """Define parameter definitions"""

        # Param 0: Original project name
        param0 = arcpy.Parameter(
            displayName="Input ArcGIS Pro Project (.aprx)",
            name="aprxInputName",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        param0.filter.list = ['aprx'] # Ensure only .aprx files can be selected

        # Param 1: Which layer you want to classify
        param1 = arcpy.Parameter(
            displayName="Layer to Classify",
            name="LayertoClassify",
            datatype="GPString", # Changed to string so users can type the layer name easily
            parameterType="Required",
            direction="Input"
        )

        # [FIX 2] Param 2: Added a parameter to let users specify the field to classify
        param2 = arcpy.Parameter(
            displayName="Field to Classify",
            name="FieldtoClassify",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        # [FIX 2] Param 3: Added a parameter for users to choose the map type (ValueList filter)
        param3 = arcpy.Parameter(
            displayName="Map Type",
            name="MapType",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        param3.filter.type = "ValueList"
        param3.filter.list = ["Graduated Colors", "Unique Values"]

        # Param 4: Output folder location
        param4 = arcpy.Parameter(
            displayName="Output Folder Location",
            name="OutputLocation",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        # Param 5: Output project name
        param5 = arcpy.Parameter(
            displayName="Output Project Name",
            name="OutputProjectName",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        params = [param0, param1, param2, param3, param4, param5]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # Retrieve user inputs from the parameters
        in_project = parameters[0].valueAsText
        in_layer = parameters[1].valueAsText
        in_field = parameters[2].valueAsText
        map_type = parameters[3].valueAsText
        out_folder = parameters[4].valueAsText
        out_name = parameters[5].valueAsText

        # Define Progressor Variables
        readTime = 2      # the time for users to read the progress
        start = 0         # beginning position of the progressor
        max = 100         # end position
        step = 33         # the progress interval to move the progressor along

        # Setup Progressor
        arcpy.SetProgressor("step", "Validating Project File...", start, max, step)
        time.sleep(readTime)  # pause the execution

        # Add Message to the Results Pane
        arcpy.AddMessage("Validating Project File...")

        # Project File
        project = arcpy.mp.ArcGISProject(in_project)

        # [FIX 3] Grabs the First Instance of a Map from the .aprx safely without hardcoding 'Map'
        campus = project.listMaps()[0]

        # Increment Progressor
        arcpy.SetProgressorPosition(start + step)  # now is 33% completed
        arcpy.SetProgressorLabel(f"Finding map layer: {in_layer}...")
        time.sleep(readTime)
        arcpy.AddMessage("Finding your map layer...")

        # Variable to check if layer is found
        layer_found = False

        # Loop Through the Layers of the Map
        for layer in campus.listLayers():
            # Check if the Layer is a Feature Layer and matches the input name
            if layer.isFeatureLayer and layer.name == in_layer:
                layer_found = True
                
                # Copy the Layer's Symbology
                symbology = layer.symbology

                # Make sure the symbology has renderer attribute
                if hasattr(symbology, 'renderer'):
                    # Increment Progressor
                    arcpy.SetProgressorPosition(start + step * 2)  # now is 66% completed
                    arcpy.SetProgressorLabel(f"Applying {map_type} to field '{in_field}'...")
                    time.sleep(readTime)
                    arcpy.AddMessage(f"Applying {map_type} classification...")

                    # [FIX 3] Dynamic logic based on user's map type selection
                    if map_type == "Graduated Colors":
                        # Update the Copy's Renderer to "Graduated Colors Renderer"
                        symbology.updateRenderer('GraduatedColorsRenderer')
                        # Correct spelling as reminded by Canvas: classificationField
                        symbology.renderer.classificationField = in_field
                        symbology.renderer.breakCount = 5
                        
                        # Try to set Color Ramp (fallback to default if 'Oranges' is not available)
                        try:
                            symbology.renderer.colorRamp = project.listColorRamps('Oranges (5 Classes)')[0]
                        except:
                            pass
                            
                    elif map_type == "Unique Values":
                        # Update the Copy's Renderer to "Unique Value Renderer"
                        symbology.updateRenderer('UniqueValueRenderer')
                        symbology.renderer.fields = [in_field]

                    # Set the Layer's Actual Symbology Equal to the Copy's
                    layer.symbology = symbology
                    arcpy.AddMessage("Finished Generating Layer Symbology.")
                
                # Exit the loop once the correct layer is processed
                break 

        # If the loop finishes and no layer was found
        if not layer_found:
            arcpy.AddError(f"Could not find a feature layer named '{in_layer}'.")
            return

        # Increment Progressor for saving
        arcpy.SetProgressorPosition(start + step * 3)  # now is 99% completed
        arcpy.SetProgressorLabel("Saving Output Project...")
        time.sleep(readTime)
        arcpy.AddMessage("Saving Output Project...")

        # Construct final output path
        out_path = out_folder + "\\" + out_name
        if not out_path.endswith(".aprx"):
            out_path += ".aprx"

        # Save the new project
        project.saveACopy(out_path)

        # Finish progressor
        arcpy.SetProgressorPosition(max)
        arcpy.SetProgressorLabel("Done!")
        arcpy.AddMessage("Map generation toolbox executed successfully!")
        
        return