import numpy as np

variables_to_drop = [
    "RF_BC",
    "RF_C2F6",
    "RF_CCl4",
    "RF_CF4",
    "RF_CFC11",
    "RF_CFC113",
    "RF_CFC114",
    "RF_CFC115",
    "RF_CFC12",
    "RF_CH3Br",
    "RF_CH3CCl3",
    "RF_CH3Cl",
    "RF_H2O_strat",
    "RF_HCFC141b",
    "RF_HCFC142b",
    "RF_HCFC22",
    "RF_HFC125",
    "RF_HFC134a",
    "RF_HFC143a",
    "RF_HFC227ea",
    "RF_HFC23",
    "RF_HFC245fa",
    "RF_HFC32",
    "RF_HFC4310",
    "RF_N2O",
    "RF_NH3",
    "RF_O3_trop",
    "RF_OC",
    "RF_SF6",
    "RF_SO2",
    "RF_aci",
    "RF_albedo",
    "RF_halon1211",
    "RF_halon1301",
    "RF_halon2402",
    "RF_misc",
    "RF_vol",
    "hc_concentration",
    "N2O_concentration",
    "O3_concentration",
    "CH4_concentration",
    "slr",
    "sl_rc",
    "sl_rc_no_ice",
]

conversion_CtoCO2 = 44.01 / 12.011  # C to CO2


def add_years_after_deployment(df, deployment_year):
    df["years_after_deployment"] = df["year"] - deployment_year


def drop_variables(df, variables_to_drop=variables_to_drop, spinup_cutoff=-100):
    df_short = df.drop_vars(variables_to_drop)

    threshold_year = df_short.year[df_short["years_after_deployment"] >= spinup_cutoff].values[0]
    df_short = df_short.where(df_short.year >= threshold_year, drop=True)
    return df_short


def calculate_new_variables(df, concentration_driven):
    # New variables
    df["fast_c"] = (
        df["LL_ocean_c"]
        + df["HL_ocean_c"]
        + df["IO_ocean_c"]
        + df["veg_c"]
        + df["detritus_c"]
        + df["soil_c"]
        + df["atmos_co2"]
    )
    df["slow_c"] = df["DO_ocean_c"] + df["earth_c"]

    # Changes over time
    df["delta_atmos_co2"] = df["atmos_co2"] - df["atmos_co2"].values[0]
    df["delta_ocean_c"] = df["ocean_c"] - df["ocean_c"].values[0]
    df["delta_LL_ocean_c"] = df["LL_ocean_c"] - df["LL_ocean_c"].values[0]

    # Unit conversions
    df["delta_atmos_co2_GtCO2"] = df["delta_atmos_co2"] * conversion_CtoCO2
    df["delta_ocean_GtCO2"] = df["delta_ocean_c"] * conversion_CtoCO2
    df["delta_LL_ocean_GtCO2"] = df["delta_LL_ocean_c"] * conversion_CtoCO2

    # Implied impact on atmosphere if concentration driven simulation
    if concentration_driven:
        df["ocean_uptake_c"] = np.cumsum(df.ocean_uptake)
        df["implied_delta_atmos_co2"] = -df["ocean_uptake_c"]

        df["implied_delta_atmos_co2_GtCO2"] = df["implied_delta_atmos_co2"] * conversion_CtoCO2
        df["ocean_uptake_GtCO2"] = df["ocean_uptake_c"] * conversion_CtoCO2


def condense_output(
    df,
    deployment_year,
    concentration_driven=False,
    spinup_cutoff=-100,
    variables_to_drop=variables_to_drop,
):
    add_years_after_deployment(df=df, deployment_year=deployment_year)

    df_short = drop_variables(df=df, variables_to_drop=variables_to_drop)

    calculate_new_variables(df=df_short, concentration_driven=concentration_driven)

    return df_short
