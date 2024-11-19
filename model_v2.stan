data {
    int n_teams; // unique teams in the dataset
    int n_games; // unique games in the dataset
    int n_seasons; // unique seasons in the dataset
    int n_leagues;

    array[n_games] int<lower=0, upper=n_seasons> season; // indexer for seasons
    array[n_games] int<lower=0, upper=n_teams> home_team_code; // home team index
    array[n_games] int<lower=0, upper=n_teams> away_team_code; // away team index
    array[n_games] int<lower=0, upper=n_leagues> league_code; // league index

    array[n_games] int home_goals; // home goals scored in match
    array[n_games] int away_goals; // away goals scored in match

    array[n_games] int home; // 1 if home, 0 o.w.
    array[n_games] int away; // 1 if away, 0 o.w.

    array[n_games] real home_xg; // home xG totaled in match
    array[n_games] real away_xg; // away xG totaled in match
}

parameters {
    matrix[n_teams, n_seasons] theta_off; // offensive team xG strength
    matrix[n_teams, n_seasons] theta_def; // defensive team xG strength

    real<lower=0> sigma_off_xg; // offensive team sd for xg
    real<lower=0> sigma_def_xg; // defensive team sd for xg
    real<lower=0> sigma_leagues; // std term for leagues

    vector[n_leagues] league_intercept; // league-specific offsets
    real<lower=0> home_xg_intercept; // home team xG intercept
    real<lower=0> away_xg_intercept; // away team xG intercept

    real<lower=0, upper=1> gamma_theta; // strength of team xG autoregressive term
}

model {
    array[n_games] real Ey_home;
    array[n_games] real Ey_away;

    // Priors

    home_xg_intercept ~ normal(1.5, 0.2);
    away_xg_intercept ~ normal(1.5, 0.2);

    gamma_theta ~ uniform(0, 1);

    sigma_off_xg ~ exponential(5);
    sigma_def_xg ~ exponential(5);
    sigma_leagues ~ exponential(5);

    for (l in 1:n_leagues) {
        league_intercept[l] ~ normal(0, sigma_leagues);
    }

    // Offense:
    for (t in 1:n_teams) {
        theta_off[t, 1] ~ normal(0, sigma_off_xg);
        for(s in 2:n_seasons){
            theta_off[t, s] ~ normal(gamma_theta * theta_off[t, s - 1], sigma_off_xg);
        }
    }
    // Defense:
    for (t in 1:n_teams) {
        theta_def[t, 1] ~ normal(0, sigma_def_xg);
        for(s in 2:n_seasons){
            theta_def[t, s] ~ normal(gamma_theta * theta_def[t, s - 1], sigma_def_xg);
        }
    }

    // likelihood:

    for (g in 1:n_games) {

        Ey_home[g] = home_xg_intercept * home[g] + theta_off[home_team_code[g], season[g]] - theta_def[away_team_code[g], season[g]] + league_intercept[league_code[g]];
        Ey_away[g] = away_xg_intercept * away[g] + theta_off[away_team_code[g], season[g]] - theta_def[home_team_code[g], season[g]] + league_intercept[league_code[g]];

    }

    // clip expected values at 0.05
    for (g in 1:n_games) {
        if (Ey_home[g] < 0.05) {
           Ey_home[g] = 0.05;
        }

        if (Ey_away[g] < 0.05) {
           Ey_away[g] = 0.05;
        }
    }

    home_goals ~ poisson(Ey_home);
    away_goals ~ poisson(Ey_away);
}