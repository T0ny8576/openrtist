import os
import numpy as np
import matplotlib.pyplot as plt
from plot_trial import *

BASEDIR = os.path.dirname(os.path.abspath(__file__))


def plot_comparison(data_to_compare, config_names, title, output_file):
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
    ax.set_xticks(x, config_names, fontsize=5)
    ax.set_ylabel('Time (ms)')
    ax.set_title(title)

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
    data_240p_folders = ["wifi_cloudlet_240p/", "wifi_aws_240p/",
                         "tmobile_cloudlet_240p/", "tmobile_aws_240p/",
                         "cbrs_cloudlet_new_240p/", "cbrs_aws_new_240p/",
                         "python_client_wifi_cloudlet_240p/", "python_client_wifi_aws_240p/",
                         "python_client_tmobile_cloudlet_240p/", "python_client_tmobile_aws_240p/",
                         "python_client_cbrs_cloudlet_240p/", "python_client_cbrs_aws_240p/"]
    data_240p = [plot_trial("Server-Log.txt", "Client-Timing.txt",
                            os.path.join(BASEDIR, "logs/", data_folder), False)
                 for data_folder in data_240p_folders]
    trial_names = ["Wi-Fi\nCloudlet\nAndroid", "Wi-Fi\nAWS\nAndroid",
                   "T-Mobile\nCloudlet\nAndroid", "T-Mobile\nAWS\nAndroid",
                   "CBRS\nCloudlet\nAndroid", "CBRS\nAWS\nAndroid",
                   "Wi-Fi\nCloudlet\nPython", "Wi-Fi\nAWS\nPython",
                   "T-Mobile\nCloudlet\nPython", "T-Mobile\nAWS\nPython",
                   "CBRS\nCloudlet\nPython", "CBRS\nAWS\nPython"]
    plot_comparison(data_240p, trial_names, "Application Response Time Comparison - 240p",
                    os.path.join(BASEDIR, "logs/", "breakdown_comparison_240p.png"))

    # data_480p_folders = ["wifi_cloudlet_480p/", "wifi_aws_480p/",
    #                      "tmobile_cloudlet_480p/", "tmobile_aws_480p/",
    #                      "cbrs_cloudlet_480p/", "cbrs_aws_480p/"]
    # data_480p = [plot_trial("Server-Log.txt", "Client-Timing.txt",
    #                         os.path.join(BASEDIR, "logs/", data_folder), False)
    #              for data_folder in data_480p_folders]
    # trial_names = ["Wi-Fi\nCloudlet\nAndroid", "Wi-Fi\nAWS\nAndroid",
    #                "T-Mobile\nCloudlet\nAndroid", "T-Mobile\nAWS\nAndroid",
    #                "CBRS\nCloudlet\nAndroid", "CBRS\nAWS\nAndroid"]
    # plot_comparison(data_480p, trial_names, "Application Response Time Comparison - 480p",
    #                 os.path.join(BASEDIR, "logs/", "breakdown_comparison_480p.png"))
