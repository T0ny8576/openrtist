import os
import numpy as np
import matplotlib.pyplot as plt
from plot_trial import *

BASEDIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    tmobile_cloudlet_data = plot_trial("Server-Log.txt",
                                       "Client-Timing.txt",
                                       os.path.join(BASEDIR, "logs/", "tmobile_cloudlet_240p/"),
                                       False)
    tmobile_aws_data = plot_trial("Server-Log.txt",
                                  "Client-Timing.txt",
                                  os.path.join(BASEDIR, "logs/", "tmobile_aws_240p/"),
                                  False)

    # TODO: Group the bars! Use pandas, or use another plot library (Seaborn?)
    full_data = [tmobile_cloudlet_data, tmobile_aws_data]
    x_ticks = ["T-Mobile Cloudlet", "T-Mobile AWS"]
    labels = ["client_pre", "net_uplink", "server_pre", "server_infer",
              "server_post", "net_downlink", "client_post"]
    colors = ["red", "orange", "green", "cyan", "blue", "yellow", "magenta"]
    y_data = np.stack([data[0] for data in full_data]).T
    y_errors = np.stack([data[2] for data in full_data]).T
    x = np.arange(len(x_ticks))
    fig, ax = plt.subplots()
    ax.set_xticks(x, x_ticks)
    ax.set_ylabel('Time (ms)')
    ax.set_title('Application Response Time Comparison - 240p')

    bottom = np.zeros(len(x_ticks))
    for i in range(len(labels)):
        p = ax.bar(x, y_data[i], label=labels[i], yerr=y_errors[i], capsize=3, bottom=bottom, color=colors[i])
        bottom += y_data[i]
    for x_pos in range(len(x_ticks)):
        ax.text(x_pos, bottom[x_pos], round(np.sum(y_data, axis=0)[x_pos]), ha='center', fontsize=10)

    # Reorder the labels in the legend
    handles, lbs = ax.get_legend_handles_labels()
    handles.reverse()
    lbs.reverse()
    ax.legend(handles, lbs, loc="upper right")
    fig.savefig(os.path.join(BASEDIR, "logs/", "breakdown_comparison.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
