import etl
import constants as c
import os
from typing import Tuple

import pandas as pd
import pymc as pm
import nutpie
import arviz as az
import pickle

def sample_team_strength_model(model_data: dict, coords: dict) -> Tuple[pm.Model, az.InferenceData]:
    """
    Creates and samples a PyMC model for team strengths.

    Parameters
    ----------
    model_data : dict
        Dictionary containing the model data.
    coords : dict
        Dictionary containing the coordinates for the model.

    Returns
    -------
    Tuple[pm.Model, az.InferenceData]
        The PyMC model and the inference data (trace).
    """

    with pm.Model(coords=coords) as model:

        ## Data
        home_idx = model_data["home_team_code"]
        away_idx = model_data["away_team_code"]
        league_idx = model_data["league_code"]

        home_xg = model_data["home_xg"]
        away_xg = model_data["away_xg"]

        ## Parameters
        gamma_att = pm.Exponential("gamma_off", lam=1)
        gamma_def = pm.Exponential("gamma_def", lam=1)

        theta_att = pm.Normal("theta_att", mu=0, sigma=gamma_att, dims="teams")
        theta_def = pm.Normal("theta_def", mu=0, sigma=gamma_def, dims="teams")

        psi_home_adv = pm.Normal("psi_home_adv", mu=0.2, sigma=0.1)
        mu_goals = pm.Normal("mu_goals", mu=1.3, sigma=0.15, dims="leagues")

        goals_home = pm.Deterministic("goals_home", mu_goals[league_idx] + psi_home_adv + theta_att[home_idx] - theta_def[away_idx])
        goals_away = pm.Deterministic("goals_away", mu_goals[league_idx] + theta_att[away_idx] - theta_def[home_idx])

        eta_match = pm.Exponential("eta_match", lam=3)

        ## Likelihooda
        obs_home_goals = pm.TruncatedNormal("obs_home_goals", mu=goals_home, sigma=eta_match, observed=home_xg)
        obs_away_goals = pm.TruncatedNormal("obs_away_goals", mu=goals_away, sigma=eta_match, observed=away_xg)

    with model:
        trace = pm.sample(nuts_sampler="nutpie")

    return model, trace

def save_artifacts(model: pm.Model, trace: az.InferenceData) -> None:
    """Saves the artifacts from a pymc model

    Parameters
    ----------
    model : pm.Model
        The model to pickle
    trace : az.InferenceData
        The model trace to save to netcdf
    """

    if not os.path.exists(c.ARTIFACTS):
        os.makedirs(c.ARTIFACTS)

    trace.to_netcdf(c.TRACE_PATH)

    with open(c.MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

def main():
    raw_data = pd.read_csv("match_data.csv")
    model_data, coords = etl.format_data_for_stan(input_df=raw_data)
    model, trace = sample_team_strength_model(model_data=model_data, coords=coords)
    save_artifacts(model=model, trace=trace)

if __name__ == "__main__":
    main()
