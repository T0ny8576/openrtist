import os
import numpy as np
import matplotlib.pyplot as plt

BASEDIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_LOG = os.path.join(BASEDIR, "log-client111.txt")


if __name__ == "__main__":
    client_gen = []

    with open(CLIENT_LOG, "r") as client_log:
        client_lines = client_log.readlines()
        for cl in client_lines:
            cls = cl.split()
            if cls[0] == "1" or cls[0] == "2":
                continue
            if "Gen" in cl:
                client_gen.append(int(cls[-1]))

    num_frames = len(client_gen)
    print(num_frames)
    client_gen = client_gen[:num_frames]

    client_gen_fps = [1000. / (client_gen[i+1] - client_gen[i]) for i in range(num_frames - 1)]

    fig, ax = plt.subplots()
    ax.set_xlabel('Frame Id')
    ax.set_xlim(0, num_frames)
    ax.set_ylabel('FPS')
    fig.set_figwidth(60)

    num_chosen = num_frames - 1
    p = ax.bar(np.arange(num_chosen), client_gen_fps[:num_chosen], width=1.)
    for i in range(num_chosen):
        ax.text(i, client_gen_fps[:num_chosen][i], int(client_gen_fps[:num_chosen][i]), ha='center', fontsize=10)
    fig.savefig(os.path.join(BASEDIR, "log-client111_src_fps.png"), dpi=300, bbox_inches="tight")
