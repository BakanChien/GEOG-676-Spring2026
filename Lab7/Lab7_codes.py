#Lab 7 Raster analysis
import arcpy

# 1.set the path
source = r"C:\GEOG-676-Spring2026\Lab7"

# 2. Assign bands: B1, B2, B3, B4
band1 = arcpy.sa.Raster(source + r"\B1.tif") # Blue
band2 = arcpy.sa.Raster(source + r"\B2.tif") # Green
band3 = arcpy.sa.Raster(source + r"\B3.tif") # Red
band4 = arcpy.sa.Raster(source + r"\B4.tif") # NIR

# 3. Composite Bands
# Name the output_combined.tif
combined = arcpy.management.CompositeBands([band1, band2, band3, band4], source + r"\output_combined.tif")

# 4. Hillshade 
# illustions: 方位角(azimuth) 315, 高度(altitude) 45
azimuth = 315
altitude = 45
shadows = "NO_SHADOWS"
z_factor = 1

# Use DEM.tif 
arcpy.ddd.HillShade(source + r"\DEM.tif", source + r"\output_Hillshade.tif", azimuth, altitude, shadows, z_factor)

# 5. Slope 
output_measurement = "DEGREE"
z_factor = 1

arcpy.ddd.Slope(source + r"\DEM.tif", source + r"\output_Slope.tif", output_measurement, z_factor)

print("success!")