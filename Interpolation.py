# 09/11/2023 - LH - Created EEvoCAN.py
# Holds helper functions for linear and bilinear interpolation operations.
# Basic interpolation functions are supplemented by more complicated functions that will fill lists with '' values by appropriate interpolation techniques.
from scipy.interpolate import CloughTocher2DInterpolator
from scipy import ndimage
import numpy as np
import matplotlib.pyplot as plt

class Interpolation:
    # Takes an 1 dimensional list of numbers and '' elements and replaces '' elements with interpolations to next value. Requires that at least the first and last elements of the list are populated.
    def LinearFill(listToFill):
        # Check that the given list is valid.
        if (len(listToFill) < 2):
            print("Unable to interpolate because list was too short.")
            return listToFill
        lastElement = listToFill[len(listToFill) - 1]
        if (str(lastElement).strip() == ''):
            print("Unable to interpolate because last element was null.")
            return listToFill
        if (str(listToFill[0]).strip() == ''):
            print("Unable to interpolate because first element was null.")
            return listToFill
        # Check to see if multiple interpolate operations are required.
        numberCount = 0
        nullCount = 0
        for i in range(0, len(listToFill)):
            if (str(listToFill[i]).strip() != ''):
                numberCount += 1
            else:
                nullCount += 1
        if (nullCount == 0):
            print("Unable to interpolate because no \"null\" elements in given list.")
            return listToFill
        if (numberCount <= 2):
            # Only one operation is required and the whole range is a valid start.
            return Interpolation.LinearInterpolate(listToFill, nullCount)
        else:
            # Locate runs of nulls.
            newList = []
            runStarted = False
            runStartAt = 0
            runEndAt = 0
            runCount = 0
            for i in range(0, len(listToFill)):
                if (str(listToFill[i]).strip() == '' and not runStarted):
                    # Run started.
                    runStarted = True
                    runStartAt = i-1
                    runCount += 1
                elif (str(listToFill[i]).strip() != '' and runStarted):
                    # Run stopped.
                    runStarted = False
                    runEndAt = i
                    newList.extend(Interpolation.LinearInterpolate(listToFill[runStartAt:runEndAt+1:], runCount)[1::])
                    runCount = 0
                elif (runStarted):
                    runCount += 1
                else:
                    newList.append(listToFill[i])
            # All runs done now piece them together with the beginning and the ends.
            return newList

    # Takes a list with '' elements and numbers at either end. Interpolates between the two numbers and replaces '' elements. Sanitise all data beforehand.
    def LinearInterpolate(listToInterpolate, nullCount):
        # All data is sanitised beforehand, but we might have no nulls to fill.
        if (nullCount == 0):
            print("Unable to interpolate because no \"null\" elements in given list.")
            return listToInterpolate
        # Get the difference between the first and last element. Assume last element is greater.
        difference = float(listToInterpolate[len(listToInterpolate) - 1]) - float(listToInterpolate[0])
        # Get the actual direction.
        increasing = True
        if (difference < 0):
            increasing = False
        # Calculate the step.
        step = difference / (nullCount + 1)
        # Fill nulls.
        for i in range(0, nullCount):
            listToInterpolate[i + 1] = float(listToInterpolate[0]) + ((i + 1)*step)
            print(f"Filling null {i+1} with value {listToInterpolate[i + 1]}.")
        # Return the updated list.
        return listToInterpolate
    
    # Takes a 2 dimensional array of points with at least 4 values and fills in the missing values by 3rd order interpolation
    def HomogenousBilinearInterpolation(tableOfValues):
        # Strip blank elements from array
        newTable = []
        for row in tableOfValues:
            newRow = []
            for element in row:
                if(str(element).strip() != ''):
                    newRow.append(float(element))
            if(len(newRow) > 0): newTable.append(newRow)

        # Convert to nparray
        npArray = np.array(newTable)
        
        # Check for homogenous array shape.
        if (npArray.dtype is np.dtype('object')):
            print("Can't interpolate: Array is not homogenous in shape.")
            return
        
        # For each blank element in array, calculate value from map of nparray.
        interpolatedTable = []
        totalRows = len(tableOfValues)
        totalColumns = len(tableOfValues[0])
        npArraySize = len(npArray[0])
        rowCount = -1
        columnCount = -1
        for row in tableOfValues:
            newRow = []
            rowCount += 1
            columnCount = -1
            for element in row:
                columnCount += 1
                if(str(element).strip() == ''):
                    xCoord = (columnCount/totalColumns)*(npArraySize-1)
                    yCoord = (rowCount/totalRows)*(npArraySize-1)
                    newRow.append(ndimage.map_coordinates(npArray.T, [[xCoord],[yCoord]], order=1)[0])
                else:
                    newRow.append(element)
            interpolatedTable.append(newRow)

        # Return the rebuilt table.
        return interpolatedTable
    
    # Takes a 2 dimensional array of points with at least 4 values and fills in the missing values by Clough Tocher 2D interpolation
    def ScatteredBicubicInterpolation(tableOfValues, colMax, rowMax):
        points = []
        values = []
        rowCount = -1
        # Find the points that are populated in the table.
        for row in tableOfValues:
            rowCount += 1
            columnCount = -1
            for element in row:
                columnCount += 1
                if(str(element).strip() != ''):
                    points.append((float(columnCount), float(rowCount)))
                    values.append(float(element))
        if (len(values) < 0):
            print ("Can't perform an interpolation if no values are entered.")
            return
        maxValue = max(values)
        

        # Check to see if there is enough information to construct initial simplex.
        if ((0, 0) not in points):
            points.append((-1,-1))
            values.append(0)
        if ((0, rowMax-1) not in points):
            points.append((-1,rowMax))
            values.append(0)
        if ((colMax-1,0) not in points):
            points.append((colMax,-1))
            values.append(0)
        if ((colMax-1, rowMax-1) not in points):
            points.append((colMax,rowMax))
            values.append(0)

        # Create an interpolator for all points.
        interp = CloughTocher2DInterpolator(points, values)

        # For each blank element in array, calculate value from interpolator.
        interpolatedTable = []
        for row in range(rowMax):
            interpolatedTable.append([])
            for column in range(colMax):
                newValue = float("{:.3f}".format(float(interp(column, row))))
                if (newValue < 0):
                    newValue = 0
                if (newValue > maxValue):
                    newValue = maxValue
                interpolatedTable[row].append(newValue)
        return interpolatedTable

        # 
        # rng = np.random.default_rng()
        # x = rng.random(10) - 0.5
        # y = rng.random(10) - 0.5
        # z = np.hypot(x, y)
        # X = np.linspace(0,columnCount)
        # Y = np.linspace(0, rowCount)
        # X, Y = np.meshgrid(X, Y)  # 2D grid for interpolation
        # Z = interp(X, Y)
        # plt.pcolormesh(X, Y, Z, shading='auto')
        # #plt.plot(points, "ok", label="input point")
        # plt.legend()
        # plt.colorbar()
        # plt.axis("equal")
        # plt.show()