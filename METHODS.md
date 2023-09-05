To demonstrate how direct air capture (DAC) and direct ocean removal (DOR) have distinct interactions with the carbon cycle, we ran several idealized model experiments in the Hector model.

## Hector model description

Hector is a simple climate model, with a globally-aggregated carbon cycle. The carbon cycle consists of one atmosphere carbon pool, four ocean carbon pools (deep ocean, intermediate ocean, low latitude surface ocean, and high latitude surface ocean), four land carbon pools (vegetation, detritus, and soil), and one earth carbon pool which represents geologic storage. The carbon cycle is described in detail in [Hartin et al. 2015](https://doi.org/10.5194/gmd-8-939-2015) and [Hartin et al. 2016](https://doi.org/10.5194/bg-13-4329-2016), as well as on the Hector [website](https://jgcri.github.io/hector/index.html). Hector is open-source and available on [Github](https://github.com/JGCRI/hector).

## Modifications to Hector code

We made several modifications to the Hector code so that we could simulate DOR. Our modified code is available on [Github](https://github.com/carbonplan/normalizing-cdr-accounting/).

First, we added an experimental implementation of DOR, which uses a hardcoded flag `ocean_cdr`. If this flag is false, the model applies the DACCS/CDR input time series as DAC (which is how the default Hector model works), such that 1 ton of carbon removal means that 1 ton of carbon is moved from the atmosphere box to the geologic storage box. If this flag is true, the model applies the DACCS/CDR input time series as DOR, such that 1 ton of carbon removal means that 1 ton of carbon is moved from the low latitude surface ocean box to the geologic storage box. We can think of this as an idealized implementation of DOR, where inorganic carbon is removed from all of the low latitude (LL) surface ocean at once, rather than from one specific location. Because of the modularity of Hector, DAC is deployed at the beginning of the year (which means it can feedback on other carbon pools throughout the year), while DOR is deployed at the end of the year (so air-sea gas exchange does not respond until the beginning of the next year). We deal with this time step discrepancy in postprocessing.

Second, we made a small modification to how Hector runs simulations when the atmospheric CO₂ concentration constraint is turned on. This change only affects simulations with fixed atmospheric CO₂ concentrations. When the atmospheric CO₂ concentration constraint is turned on, the default Hector model calculates the difference between its calculated atmospheric CO₂ and the prescribed CO₂ constraint (i.e. the residual), and then forces the atmospheric CO₂ to meet the prescribed constraint by transferring carbon between the atmosphere to the deep ocean carbon pool. This transfer does not represent any realistic process, and was designed to achieve conservation of mass, with the reasoning that the deep ocean carbon reservoir is very large so changes in this large pool would not affect carbon cycle dynamics much ([Hartin et al. 2015](https://doi.org/10.5194/gmd-8-939-2015)). We changed this so that the prescribed CO₂ constraint is instead met by adjusting the calculated atmospheric CO₂, but without adding/subtracting the residual from any other carbon pool. This breaks the conservation of mass so should not be implemented outside of this kind of experimental context, but it allows us to more accurately diagnose how the ocean would respond to a direct ocean removal over time.

Our modeling workflow involves making a few hardcoded changes to the code. To toggle between CDR being implemented as DAC or DOR, we manually change the `ocean_cdr` flag. To demonstrate how the rate of air-sea gas exchange influences the timing and magnitude of atmospheric drawdown from DOR, we manually change the low-latitude surface ocean windspeed (`surfaceLL.mychemistry.U`).

## Model experiments

We simulated one-year pulse removals and emissions of carbon, such that the removal or emission occurs in the context of a constant, preindustrial background climate state. These are idealized simulations, designed to illustrate global-scale equilibration dynamics rather than to accurately simulate reality. We note that the fraction of CO₂ removed which stays out of the atmosphere (i.e. CDR effectiveness) depends on the emissions trajectory and mean climate state, such that CDR effectiveness decreases under lower CO₂ concentrations. We therefore expect the outgassing from land and carbon pools in these simulations is larger than one would expect if CDR were deployed at present day. These differences do not affect relative comparisons of the temporal and carbon cycle dynamics of DAC and DOR.

We ran two kinds of model experiments: emissions-driven runs (where changing land and ocean carbon fluxes can influence atmospheric CO₂ concentrations) and concentration-driven simulations (where atmospheric CO₂ concentrations are prescribed and not influenced by land and ocean carbon fluxes). For the emissions-driven runs, we held CO₂ emissions constant over time at 0 tons of carbon per year. For the concentration-driven runs, we held atmospheric CO₂ concentrations constant at 277.15 ppm, which is consistent with the atmospheric CO₂ concentration in the emissions-driven preindustrial simulation.

We ran the following model experiments to generate data for the article:
| Experiment Name | CDR Pathway | Carbon Cycle Feedbacks | Parameters Used
| :---------------- | :------: | :----: |:---- |
| DOR_concentrationDriven | DOR | Off | Default parameters
| DOR_concentrationDriven_lowWind | DOR | Off | LL Wind = 3 m/s
| DOR_concentrationDriven_highWind | DOR | Off | LL Wind = 11 m/s
| DOR_emissionsDriven | DOR | On | Default parameters
| DAC_emissionsDriven | DAC | On | Default parameters

We did not simulate the concentration-driven DAC simulation because there is no physical mechanism through which DAC can influence other components of the carbon cycle when carbon cycle feedbacks are turned off.

For all simulations, Hector was run through the model default concentration-driven spin up procedure, and then we ran Hector for another 4,000 years. For the first 2,000 years, Hector was run at constant preindustrial forcing to ensure that all carbon pools were equilibrated. One-year pulse emissions and removals were then applied, followed by another 2,000 years of constant preindustrial forcing to track how the perturbation propagated through the Earth system over time. The exact input files we used are documented in `data/hector-forcing`.

## Post-processing model output

We did two main calculations to postprocess the raw Hector model output into data for use in visualizations. All postprocessing code is included in the project GitHub repository.

First, for concentration-driven DOR simulations, we calculated the implied change in atmospheric CO₂ from the oceanic uptake of carbon from the atmosphere. This calculation is necessary because these simulations had carbon cycle feedbacks turned off, so oceanic uptake of atmospheric CO₂ could not actually change the atmospheric CO₂ concentration within the model. We calculated this from the cumulative change in ocean dissolved inorganic carbon (DIC) over time. This is equivalent to the DIC equilibration calculation shown in [Bach et al. 2023](https://doi.org/10.1002/lol2.10330). For example, if 1 ton of carbon is removed from the ocean at year 0 (i.e. \Delta*{C, ocean} = -1 ton), and after three years 0.9 tons of carbon has been taken up by the ocean (i.e. \Delta*{C, ocean} = -0.1 tons) then we calculate that as a change in atmospheric CO₂ of -0.9 tons.

We also added a new variable 'years after deployment' to use as a time index, and adjusted this to account for the time step discrepancy between the model implementation of DOR and DAC.

In addition to these substantive postprocessing steps, we also post processed the raw output into smaller files for use in visualization, e.g. by discarding spin up years and unnecessary output variables not directly used in our visualizations. The raw model output files are in `data/hector-output` and the postprocessed model output files are in `data/postprocessed-hector`.

## Environment setup instructions

Hector can be installed by cloning the repository for a modified version of Hector, and checking out the experimental-ocean-cdr branch from [Github](https://github.com/carbonplan/normalizing-cdr-accounting/). If you have any questions about how to run Hector or how Hector works in general, please refer to the [Hector manual](https://jgcri.github.io/hector/index.html) or reach out to the lead Hector developers. If you have questions about the code modifications in the experimental-ocean-cdr branch, please contact Claire Zarakas (czarakas@uw.edu).

After cloning the Github repository, set `HECTOR_PATH` as an environment variable.
`export HECTOR_PATH="my/path/to/the/code/hector"`

For all analysis of Hector model output, the carbonplan-notebook docker image was used as the analysis environment and specific versions can be viewed [here](https://quay.io/repository/carbonplan/carbonplan-notebook/manifest/sha256:63d4eb6b40e0efbc21f894d7e4af97e7b972c18bc44a2a949213e0dde152f6e3?tab=packages)

## Reproducing results

Our results can be reproduced through the following steps:

1. Run Hector simulations using bash scripts in `scripts`. These scripts build and run Hector, which is written in C++, using input files in `data/hector-forcing`
2. Post-process Hector model output using Python notebook in `notebooks/2_postprocess_output.ipynb` and `notebooks/3_make_jsons_for_visualization.ipynb`
3. Make static versions of article visualizations using Python notebook in `notebooks/4_make_static_visualizations.ipynb`
