import pandas as pd
import statsmodels.api as sm
from patsy import dmatrix
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar



def get_threshold_example():
    # Data
    data = {
        'x': [1,2,3,4,5,6,7,8,9,10],
        'y': [2.1,2.5,3.7,3.9,5.1,5.5,6.7,7.4,7.9,9.0],
        'std_dev': [0.2,0.3,0.25,0.3,0.2,0.4,0.35,0.3,0.25,0.3]
    }
    df = pd.DataFrame(data)
    df['weights'] = 1 / (df['std_dev'] ** 2)

    # Spline basis for model
    x_spline = dmatrix("bs(x, df=5, degree=3, include_intercept=True)", df, return_type='dataframe')

    # Fit weighted model
    model = sm.WLS(df['y'], x_spline, weights=df['weights']).fit()

    # Predict across x range for plotting
    x_pred = pd.DataFrame({'x': np.linspace(df['x'].min(), df['x'].max(), 300)})
    x_pred_spline = dmatrix("bs(x, df=5, degree=3, include_intercept=True)", x_pred, return_type='dataframe')

    predicted = model.get_prediction(x_pred_spline)
    pred_summary = predicted.summary_frame(alpha=0.05)

    # Prediction at specific x0
    
    x0 = 6.4
    x0_df = pd.DataFrame({'x': [x0]})
    x0_spline = dmatrix("bs(x, df=5, degree=3, include_intercept=True)", x0_df, return_type='dataframe')
    x0_pred = model.get_prediction(x0_spline).summary_frame(alpha=0.05)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.errorbar(df['x'], df['y'], yerr=df['std_dev'], fmt='o', label='Data (with error)', capsize=3, color='gray')
    plt.plot(x_pred['x'], pred_summary['mean'], label='Spline prediction', color='blue')
    plt.fill_between(x_pred['x'], pred_summary['mean_ci_lower'], pred_summary['mean_ci_upper'],
                    color='blue', alpha=0.2, label='95% Confidence Interval')

    # Highlight x0 prediction
    plt.scatter([x0], x0_pred['mean'], color='red', zorder=5, label=f'Prediction at x={x0}')
    plt.errorbar([x0], x0_pred['mean'],
                yerr=[[x0_pred['mean'].values[0] - x0_pred['mean_ci_lower'].values[0]],
                    [x0_pred['mean_ci_upper'].values[0] - x0_pred['mean'].values[0]]],
                fmt='o', color='red', capsize=5)

    # Labels
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Weighted Spline Regression with 95% Confidence Interval")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def get_threshold(x_data, y_data, std_dev_data, tresh_value, show=False):
    # Data
    data = {
        'x': x_data,
        'y': y_data,
        'std_dev': std_dev_data 
    }
    df = pd.DataFrame(data)
    df['std_dev'] = df['std_dev'].fillna(0.1).clip(lower=1e-2)  # or another small floor
    df['weights'] = 1 / (df['std_dev'] ** 2)

    # print("Number of unique x values:", df['x'].nunique())
    
    # print("Min std dev:", df['std_dev'].min())

    spline_formula = "bs(x, df=5, degree=3, include_intercept=True)"
    # Spline basis for model
    x_spline = dmatrix(spline_formula, df, return_type='dataframe')
    design_info = x_spline.design_info

    # Fit weighted model
    model = sm.WLS(df['y'], x_spline, weights=df['weights']).fit()

    # Predict across x range for plotting
    x_pred = pd.DataFrame({'x': np.linspace(df['x'].min(), df['x'].max(), 300)})
    x_pred_spline = dmatrix(design_info, x_pred, return_type='dataframe')

    predicted = model.get_prediction(x_pred_spline)
    pred_summary = predicted.summary_frame(alpha=0.05)

    def model_minus_target(x):
        x_df = pd.DataFrame({'x': [x]})
        x_spline = dmatrix(design_info, x_df, return_type='dataframe')
        y_pred = model.predict(x_spline)[0]
        return y_pred - tresh_value
    try:
        x0 = root_scalar(model_minus_target, bracket=[df['x'].min(), df['x'].max()], method='brentq').root
    except:
        return [-1, [0, 0]]
    
    # feed it back in
    # Prediction at specific x0
    x0_df = pd.DataFrame({'x': [x0]})
    x0_spline = dmatrix(design_info, x0_df, return_type='dataframe')
    x0_pred = model.get_prediction(x0_spline).summary_frame(alpha=0.05)

    if show:
    # Plotting
        plt.figure(figsize=(10, 6))
        plt.errorbar(df['x'], df['y'], yerr=df['std_dev'], fmt='o', label='Data (with error)', capsize=3, color='gray')
        plt.plot(x_pred['x'], pred_summary['mean'], label='Spline prediction', color='blue')
        plt.fill_between(x_pred['x'], pred_summary['mean_ci_lower'], pred_summary['mean_ci_upper'],
                        color='blue', alpha=0.2, label='95% Confidence interval')

        # Highlight x0 prediction
        plt.scatter([x0], x0_pred['mean'], color='red', zorder=5, label=f'Prediction at x={x0}')
        plt.errorbar([x0], x0_pred['mean'],
                    yerr=[[x0_pred['mean'].values[0] - x0_pred['mean_ci_lower'].values[0]],
                        [x0_pred['mean_ci_upper'].values[0] - x0_pred['mean'].values[0]]],
                    fmt='o', color='red', capsize=5)

        # Labels
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Packet loss (%)")
        plt.title("Weighted spline regression  5% Treshold")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        print("weird")
        plt.show()
    return x0, [x0_pred['mean'].values[0] - x0_pred['mean_ci_lower'].values[0], x0_pred['mean_ci_upper'].values[0] - x0_pred['mean'].values[0]]

if __name__ == " __main__":
    get_threshold_example()