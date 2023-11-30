from CTkTable import CTkTable
from tksheet import Sheet


# Handles the resizing of the x and y values of the derate tables.
class ResizeHandler():
    chargeSocAxis: CTkTable = None
    chargeTemperatureAxis: CTkTable = None
    dischargeSocAxis: CTkTable = None
    dischargeTemperatureAxis: CTkTable = None
    chargeTable: Sheet = None
    dischargeTable: Sheet = None

    @classmethod
    def setAxisReference(cls, axis, isSoc=False, isCharge=False):
        if (isSoc):
            if (isCharge):
                cls.chargeSocAxis = axis
            else:
                cls.dischargeSocAxis = axis
        else:
            if (isCharge):
                cls.chargeTemperatureAxis = axis
            else:
                cls.dischargeTemperatureAxis = axis

    @classmethod
    def setTableReference(cls, table, isCharge=False):
        if (isCharge):
            cls.chargeTable = table
        else:
            cls.dischargeTable = table

    @classmethod
    def update_axis(cls, isCharge=False):
        # Check to see if the soc and temp axis have data everywhere.
        if (isCharge):
            for i in cls.chargeSocAxis.values[0]:
                if (str(i).strip() == ''):
                    print("Failed to update axis: "
                          "Charge SoC Axis Incomplete")
                    return
            for i in cls.chargeTemperatureAxis.values[0]:
                if (str(i).strip() == ''):
                    print("Failed to update axis: "
                          "Charge Temperature Axis Incomplete")
                    return
        else:
            for i in cls.dischargeSocAxis.values[0]:
                if (str(i).strip() == ''):
                    print("Failed to update axis: "
                          "Discharge SoC Axis Incomplete")
                    return
            for i in cls.dischargeTemperatureAxis.values[0]:
                if (str(i).strip() == ''):
                    print("Failed to update axis: "
                          "Discharge Temperature Axis Incomplete")
                    return

        # Update the relevant table.
        if (isCharge):
            cls.chargeTable.headers(
                newheaders=cls.chargeTemperatureAxis.values[0],
                redraw=True)
            cls.chargeTable.row_index(
                newindex=cls.chargeSocAxis.values[0],
                redraw=True)
            cls.chargeTable.set_sheet_data(data=[[]])
            cls.chargeTable.set_all_column_widths(30)
        else:
            cls.dischargeTable.headers(
                newheaders=cls.dischargeTemperatureAxis.values[0],
                redraw=True)
            cls.dischargeTable.row_index(
                newindex=cls.dischargeSocAxis.values[0],
                redraw=True)
            cls.dischargeTable.set_sheet_data(data=[[]])
            cls.dischargeTable.set_all_column_widths(30)

    @classmethod
    def resizeTable(cls, value: str, isSoC=False, isCharge=False):
        if (isSoC):
            if (isCharge):
                table = cls.chargeSocAxis
            else:
                table = cls.dischargeSocAxis
        else:
            if (isCharge):
                table = cls.chargeTemperatureAxis
            else:
                table = cls.dischargeTemperatureAxis

        # Check the data.
        if (value == ''):
            print(f"Not resizing because \"{value}\" is blank.")
            return
        if (not value.isnumeric()):
            print(f"Not resizing because \"{value}\" is not numeric.")
            return
        newInt = int(value)
        if (newInt < 2):
            print(f"Not resizing because \"{value}\" is too small.")
            return
        if (newInt > 101):
            print(f"Not resizing because \"{value}\" is too large.")
            return
        # Check for number at end.
        retainFinal = False
        oldColumns = table.columns
        finalNumber = str(table.get_row(0)[oldColumns-1])
        if (finalNumber != ''):
            if (finalNumber.isnumeric):
                retainFinal = True
        # Reconfigure the columns.
        print("Call to configure, redrawing")
        table.configure(columns=newInt, width=40)
        # If we need to update the end number, do that.
        if (retainFinal):
            if (oldColumns < newInt):
                table.insert(0, oldColumns-1, '')
            table.insert(0, table.columns - 1, finalNumber)
        # Update big tables
        cls.update_axis(isCharge)
