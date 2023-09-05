import numpy as np
import pandas as pd
import xarray as xr


def read_raw_hector_csv(fname, skiprows=0, filetype="C++"):
    """Reads the raw hector output file (csv) which is generated by
    running Hector in the command line
    inputs:
        - fname: filename, a csv
    outputs:
        - df: pandas dataframe
    """
    if skiprows is None:
        df = pd.read_csv(fname)
    else:
        df = pd.read_csv(fname, skiprows=[skiprows])

    if filetype == "C++":
        df["variable_component"] = df.component + "_" + df.variable
    elif filetype == "R":
        df["variable_component"] = df["variable"]
        df["run_name"] = df["scenario"]
        df["component"] = "R_output"
        df["spinup"] = 0
        df = df[df["variable"] != "earth_c"]
    return df


def process_data_to_xarray(df, printon=False):
    """Processes pandas dataframe of raw hector output (which has
    a flat structure) into an xarray
    inputs:
        - df: pandas dataframe
    outputs:
        - ds: xarray datasets
    """
    set(df.variable.values)
    variable_component_names = set(df.variable_component.values)

    for i, varcompname in enumerate(variable_component_names):
        if printon:
            print(varcompname)
        subset_variable = df[df.variable_component == varcompname]
        variables = subset_variable.variable.values
        units = subset_variable.units.values
        years = subset_variable.year.values
        data = subset_variable.value.values
        run_name = subset_variable.run_name.values
        component = subset_variable.component.values

        if i == 0:
            spinup = subset_variable.spinup.values

        # ----------------Check for errors
        if not np.size(set(variables)) == 1:
            raise AssertionError("Not all variables are the same")
        else:
            variablename = next(iter(set(variables)))

        if not np.size(set(units)) == 1:
            raise AssertionError("Not all values for this variable have the same units")
        else:
            var_units = next(iter(set(units)))

        if not np.size(set(run_name)) == 1:
            raise AssertionError("Not all values for this variable have the same run name")
        else:
            var_run_name = next(iter(set(run_name)))

        if not np.size(set(component)) == 1:
            raise AssertionError("Not all values for this variable have the same run name")
        else:
            var_component = next(iter(set(component)))

        # ----------------
        if varcompname in ["hc_concentration"]:
            varname = varcompname
        else:
            varname = variablename

        da = xr.DataArray(
            data=data,
            dims=["year"],
            coords=dict(
                year=years,
            ),
            attrs=dict(units=var_units, component=var_component, run_name=var_run_name),
        )

        if i == 0:
            ds = da.to_dataset(name=varname)
            da2 = xr.DataArray(
                data=spinup,
                dims=["year"],
                coords=dict(
                    year=years,
                ),
                attrs=dict(run_name=var_run_name),
            )
            ds["spinup"] = da2
        else:
            ds[varname] = da

    return ds


def process_csv_to_xarray(fname, startyear=1750, skiprows=0, filetype="C++"):
    """Processes raw hector output file (csv) which is generated by
    running Hector in the command line into an xarray datasets
    inputs:
        - fname: filename, a csv
        - startyear: when simulation started (this is to exclude spinup years)
    outputs:
        - ds: xarray datasets
    """

    df = read_raw_hector_csv(fname, skiprows=skiprows, filetype=filetype)
    df_postspinup = df[df.year >= startyear]
    ds = process_data_to_xarray(df_postspinup, printon=False)

    return ds