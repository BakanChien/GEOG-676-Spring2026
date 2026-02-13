import arcpy

# Cover the old file
arcpy.env.overwriteOutput = True

arcpy.env.workspace = r"C:\GEOG-676-Spring2026\Lab4\codes_env"
folder_path = r"C:\GEOG-676-Spring2026\Lab4"
gdb_name = 'Test.gdb'
gdb_path = folder_path + '\\' + gdb_name

# 1. create GDB
print("Creating GDB...")
arcpy.CreateFileGDB_management(folder_path, gdb_name)

# 2.open CSV and convert
print("Reading CSV and creating garage points...")
csv_path = r"C:\GEOG-676-Spring2026\Lab4\garages.csv"
garage_layer_name = 'Garage_Points'
garages = arcpy.MakeXYEventLayer_management(csv_path, 'X', 'Y', garage_layer_name)

arcpy.FeatureClassToGeodatabase_conversion(garages, gdb_path)
garage_points = gdb_path + '\\' + garage_layer_name

# 3. copy Campus 's bilding 
print("Copying Structures from Campus.gdb...")
campus = r'C:\GEOG-676-Spring2026\Lab4\Campus.gdb'
buildings_campus = campus + '\\Structures'
buildings = gdb_path + '\\Buildings'
arcpy.CopyFeatures_management(buildings_campus, buildings)

# 4. Re-Projection
print("Reprojecting garage points...")
spatial_ref = arcpy.Describe(buildings).spatialReference
garage_reprojected = gdb_path + '\\Garage_Points_reprojected'
arcpy.Project_management(garage_points, garage_reprojected, spatial_ref)

# 5.Create Buffer

user_distance = input("Please enter buffer distance (e.g. 150): ")
buffer_distance = f"{user_distance} Meters"
garage_buffered = gdb_path + '\\Garage_Points_buffered'
print(f"Buffering with distance: {buffer_distance}...")
arcpy.Buffer_analysis(garage_reprojected, garage_buffered, buffer_distance)

# 6. Intersect
print("Intersecting buffered garages with buildings...")
intersect_output = gdb_path + '\\Garage_Building_Intersection'
arcpy.Intersect_analysis([garage_buffered, buildings], intersect_output, 'ALL')

# 7. print CSV
print("Exporting table to CSV...")
arcpy.TableToTable_conversion(intersect_output, r'C:\GEOG-676-Spring2026\Lab4', 'nearbyBuildings.csv')

print("Success! CSV file created. Check your Lab4 folder!")