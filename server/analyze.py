import os
import numpy as np
import matplotlib.pyplot as plt

BASEDIR = os.path.dirname(os.path.abspath(__file__))
LOGDIR = os.path.join(BASEDIR, "logs/")
CLIENT_LOG = os.path.join(LOGDIR, "Client-Timing-2024-02-07-16-32-27-EST.txt")
SERVER_LOG = os.path.join(LOGDIR, "log-1707346074.txt")


def plot_histogram(data, xlabel, ylabel, fname, bins=40, dpi=300, x_range=None):
    fig, ax = plt.subplots()
    ax.hist(data, bins=bins, range=x_range)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    agg_text = "mean = {:.2f}\nmedian = {:.2f}\nstd = {:.2f}".format(np.mean(data), np.median(data), np.std(data))
    ax.text(0.75, 0.85, agg_text, transform=ax.transAxes, bbox=dict(fc='white', ec='black', alpha=0.5))
    fig.savefig(fname, dpi=dpi)
    plt.close(fig)


def plot_per_frame_metric(per_frame_data, ylabel, fname, frame_to_plot=None):
    fig, ax = plt.subplots()
    ax.set_xlabel('Frame Id')
    ax.set_ylabel(ylabel)
    if frame_to_plot is None:
        frame_to_plot = len(per_frame_data)
    ax.set_xlim(0, frame_to_plot)
    fig.set_figwidth(60)
    p = ax.bar(np.arange(frame_to_plot), per_frame_data[:frame_to_plot], width=1.)
    for i in range(frame_to_plot):
        ax.text(i, per_frame_data[:frame_to_plot][i], int(per_frame_data[:frame_to_plot][i]), ha='center', fontsize=10)
    fig.savefig(fname, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    client_gen = np.zeros((999,))
    client_send = np.zeros((999,))
    client_recv = np.zeros((999,))
    client_done = np.zeros((999,))
    server_recv = np.zeros((999,))
    server_done = np.zeros((999,))
    server_pre = np.zeros((999,))
    server_infer = np.zeros((999,))
    server_post = np.zeros((999,))
    server_total = np.zeros((999,))
    server_wait = np.zeros((999,))
    with open(CLIENT_LOG, "r") as client_log:
        client_lines = client_log.readlines()
        for cl in client_lines:
            cls = cl.split()
            if cls[0] == "1" or cls[0] == "2":
                continue
            if "Gen" in cl and "Failed" not in cl:
                client_gen[int(cls[0]) - 3] = int(cls[-1])
            elif "Send" in cl:
                client_send[int(cls[0]) - 3] = int(cls[-1])
            elif "Recv" in cl:
                client_recv[int(cls[0]) - 3] = int(cls[-1])
            elif "Done" in cl:
                client_done[int(cls[0]) - 3] = int(cls[-1])

    with open(SERVER_LOG, "r") as server_log:
        server_lines = server_log.readlines()
        for sl in server_lines:
            if len(sl.strip()) > 0:
                sls = sl.split(", ")
                if sls[0] == "#1" or sls[0] == "#2":
                    continue
                idx = int(sls[0].replace("#", "")) - 3
                server_recv[idx] = float(sls[1].replace("time = ", "")) * 1000
                server_done[idx] = float(sls[2].replace("done = ", "")) * 1000
                server_pre[idx] = float(sls[3].replace("pre = ", "").replace(" ms", ""))
                server_infer[idx] = float(sls[4].replace("infer = ", "").replace(" ms", ""))
                server_post[idx] = float(sls[5].replace("post = ", "").replace(" ms", ""))
                server_wait[idx] = float(sls[6].replace("wait = ", "").replace(" ms", ""))
                server_total[idx] = server_done[idx] - server_recv[idx]

    num_frames = sum(client_done > 0)
    print(num_frames)
    client_gen = client_gen[:num_frames]
    client_send = client_send[:num_frames]
    client_recv = client_recv[:num_frames]
    client_done = client_done[:num_frames]
    server_recv = server_recv[:num_frames]
    server_done = server_done[:num_frames]
    server_pre = server_pre[:num_frames]
    server_infer = server_infer[:num_frames]
    server_post = server_post[:num_frames]
    server_total = server_total[:num_frames]

    server_wait = server_wait[1:num_frames]
    client_fps = [1000. / (client_done[i + 1] - client_done[i]) for i in range(num_frames - 1)]

    client_pre = [client_send[fid] - client_gen[fid] for fid in range(num_frames)]
    client_post = [client_done[fid] - client_recv[fid] for fid in range(num_frames)]
    net_uplink = [server_recv[fid] - client_send[fid] for fid in range(num_frames)]
    net_downlink = [client_recv[fid] - server_done[fid] for fid in range(num_frames)]
    net_total = [net_uplink[fid] + net_downlink[fid] for fid in range(num_frames)]
    frame_total = [client_done[fid] - client_gen[fid] for fid in range(num_frames)]

    # print(net_uplink)
    # print(net_downlink)

    """ Individual histograms
    """
    plot_histogram(client_pre, 'Time (ms)', 'Frame Count', os.path.join(LOGDIR, "client_pre-CMU-SECURE.png"))
    plot_histogram(client_post, 'Time (ms)', 'Frame Count', os.path.join(LOGDIR, "client_post-CMU-SECURE.png"))
    plot_histogram(server_pre, 'Time (ms)', 'Frame Count', os.path.join(LOGDIR, "server_pre-CMU-SECURE.png"))
    plot_histogram(server_infer, 'Time (ms)', 'Frame Count', os.path.join(LOGDIR, "server_infer-CMU-SECURE.png"))
    plot_histogram(server_post, 'Time (ms)', 'Frame Count', os.path.join(LOGDIR, "server_post-CMU-SECURE.png"))
    plot_histogram(server_wait, 'Time (ms)', 'Frame Count', os.path.join(LOGDIR, "server_wait-CMU-SECURE.png"))
    plot_histogram(server_total, 'Time (ms)', 'Frame Count', os.path.join(LOGDIR, "server_total-CMU-SECURE.png"))
    plot_histogram(net_uplink, 'Latency (ms)', 'Frame Count', os.path.join(LOGDIR, "net_uplink-CMU-SECURE.png"))
    plot_histogram(net_downlink, 'Latency (ms)', 'Frame Count', os.path.join(LOGDIR, "net_downlink-CMU-SECURE.png"))
    plot_histogram(net_total, 'Latency (ms)', 'Frame Count', os.path.join(LOGDIR, "net_total-CMU-SECURE.png"))
    plot_histogram(frame_total, 'Time (ms)', 'Frame Count', os.path.join(LOGDIR, "frame_total-CMU-SECURE.png"))
    plot_histogram(client_fps, 'FPS', 'Frame Count', os.path.join(LOGDIR, "client_fps-CMU-SECURE.png"), x_range=[0, 60])

    plot_per_frame_metric(server_infer, 'Inference Time (ms)', os.path.join(LOGDIR, "gpu_infer-CMU-SECURE.png"))

    """ Stacked histograms
    fig, ax = plt.subplots()
    ax.hist(stacked.T, bins=100, label=labels, stacked=True)
    ax.set_xlabel('Latency (ms)')
    ax.set_ylabel('Frame Count')
    ax.legend(loc="upper right")
    fig.savefig(os.path.join(LOGDIR, "frame_histogram-CMU-SECURE.png"), dpi=300)
    """

    """ Stacked Distribution
    """
    stacked = np.stack([client_pre, net_uplink, server_pre, server_infer, server_post, net_downlink, client_post])
    labels = ["client_pre", "net_uplink", "server_pre", "server_infer", "server_post", "net_downlink", "client_post"]
    fig, ax = plt.subplots()
    ax.set_xlabel('Frame Id')
    ax.set_xlim(0, 1000)
    ax.set_ylabel('Latency (ms)')
    ax.set_title('End-to-end Delay Distribution per Frame')
    fig.set_figwidth(50)

    num_chosen = num_frames
    bottom = np.zeros(num_chosen)
    for i in range(len(labels)):
        p = ax.bar(np.arange(num_chosen), stacked[i][:num_chosen], width=1., label=labels[i], bottom=bottom)
        bottom += stacked[i][:num_chosen]

    # Reorder the labels in the legend
    handles, lbs = ax.get_legend_handles_labels()
    handles.reverse()
    lbs.reverse()
    ax.legend(handles, lbs, loc="upper right")
    fig.savefig(os.path.join(LOGDIR, "frame_stacked-CMU-SECURE.png"), dpi=600, bbox_inches="tight")
