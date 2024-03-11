import os
import numpy as np
import matplotlib.pyplot as plt
from plot_trial import *

BASEDIR = os.path.dirname(os.path.abspath(__file__))


def plot_comparison(data_to_compare, config_names, output_file):
    # TODO: Group the bars! Use pandas, or use another plot library (Seaborn?)
    labels = ["client_pre", "net_uplink", "server_pre", "server_infer",
              "server_post", "net_downlink", "client_post"]
    colors = ["cyan", "yellow", "green", "red", "blue", "magenta", "lime"]
    y_data = np.stack([data[0] for data in data_to_compare]).T
    error_bar_top = y_data.copy()
    y_error_lower = np.stack([data[0] - data[3] for data in data_to_compare]).T
    y_error_upper = np.stack([data[4] - data[0] for data in data_to_compare]).T
    x = np.arange(len(config_names))
    fig, ax = plt.subplots()
    ax.set_xticks(x, config_names)
    ax.set_ylabel('Time (ms)')
    ax.set_title('Application Response Time Comparison - 240p')

    bottom = np.zeros(len(config_names))
    for i in range(len(labels)):
        p = ax.bar(x, y_data[i], label=labels[i], yerr=[y_error_lower[i], y_error_upper[i]], capsize=3,
                   bottom=bottom, color=colors[i])
        bottom += y_data[i]
        error_bar_top[i] = bottom + y_error_upper[i]
    for x_pos in range(len(config_names)):
        ax.text(x_pos, np.max(error_bar_top[:, x_pos]) + 1., round(np.sum(y_data, axis=0)[x_pos]), ha='center',
                fontsize=10)

    # Reorder the labels in the legend
    handles, lbs = ax.get_legend_handles_labels()
    handles.reverse()
    lbs.reverse()
    ax.legend(handles, lbs, loc="upper left")
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    wifi_cloudlet_data_240p = plot_trial("Server-Log.txt",
                                         "Client-Timing.txt",
                                         os.path.join(BASEDIR, "logs/", "wifi_cloudlet_240p/"),
                                         False)
    wifi_aws_data_240p = plot_trial("Server-Log.txt",
                                    "Client-Timing.txt",
                                    os.path.join(BASEDIR, "logs/", "wifi_aws_240p/"),
                                    False)
    tmobile_cloudlet_data_240p = plot_trial("Server-Log.txt",
                                            "Client-Timing.txt",
                                            os.path.join(BASEDIR, "logs/", "tmobile_cloudlet_240p/"),
                                            False)
    tmobile_aws_data_240p = plot_trial("Server-Log.txt",
                                       "Client-Timing.txt",
                                       os.path.join(BASEDIR, "logs/", "tmobile_aws_240p/"),
                                       False)
    cbrs_cloudlet_data_240p = plot_trial("Server-Log.txt",
                                         "Client-Timing.txt",
                                         os.path.join(BASEDIR, "logs/", "cbrs_cloudlet_240p/"),
                                         False)
    cbrs_aws_data_240p = plot_trial("Server-Log.txt",
                                    "Client-Timing.txt",
                                    os.path.join(BASEDIR, "logs/", "cbrs_aws_240p/"),
                                    False)
    data_240p = [wifi_cloudlet_data_240p, wifi_aws_data_240p,
                 tmobile_cloudlet_data_240p, tmobile_aws_data_240p,
                 cbrs_cloudlet_data_240p, cbrs_aws_data_240p]
    trial_names = ["Wi-Fi\nCloudlet", "Wi-Fi\nAWS",
                   "T-Mobile\nCloudlet", "T-Mobile\nAWS",
                   "CBRS\nCloudlet", "CBRS\nAWS"]
    plot_comparison(data_240p, trial_names, os.path.join(BASEDIR, "logs/", "breakdown_comparison_240p.png"))

    wifi_cloudlet_data_480p = plot_trial("Server-Log.txt",
                                         "Client-Timing.txt",
                                         os.path.join(BASEDIR, "logs/", "wifi_cloudlet_480p/"),
                                         False)
    wifi_aws_data_480p = plot_trial("Server-Log.txt",
                                    "Client-Timing.txt",
                                    os.path.join(BASEDIR, "logs/", "wifi_aws_480p/"),
                                    False)
    tmobile_cloudlet_data_480p = plot_trial("Server-Log.txt",
                                            "Client-Timing.txt",
                                            os.path.join(BASEDIR, "logs/", "tmobile_cloudlet_480p/"),
                                            False)
    tmobile_aws_data_480p = plot_trial("Server-Log.txt",
                                       "Client-Timing.txt",
                                       os.path.join(BASEDIR, "logs/", "tmobile_aws_480p/"),
                                       False)
    cbrs_cloudlet_data_480p = plot_trial("Server-Log.txt",
                                         "Client-Timing.txt",
                                         os.path.join(BASEDIR, "logs/", "cbrs_cloudlet_480p/"),
                                         False)
    cbrs_aws_data_480p = plot_trial("Server-Log.txt",
                                    "Client-Timing.txt",
                                    os.path.join(BASEDIR, "logs/", "cbrs_aws_480p/"),
                                    False)
    data_480p = [wifi_cloudlet_data_480p, wifi_aws_data_480p,
                 tmobile_cloudlet_data_480p, tmobile_aws_data_480p,
                 cbrs_cloudlet_data_480p, cbrs_aws_data_480p]
    trial_names = ["Wi-Fi\nCloudlet", "Wi-Fi\nAWS",
                   "T-Mobile\nCloudlet", "T-Mobile\nAWS",
                   "CBRS\nCloudlet", "CBRS\nAWS"]
    plot_comparison(data_480p, trial_names, os.path.join(BASEDIR, "logs/", "breakdown_comparison_480p.png"))
