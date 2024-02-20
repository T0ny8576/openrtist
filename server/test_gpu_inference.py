from torch.autograd import Variable
from transformer_net import TransformerNet
from torchvision import transforms
import numpy as np
import torch
import os
import matplotlib.pyplot as plt
import time

BASEDIR = os.path.dirname(os.path.abspath(__file__))
GPU_BOOST_CLOCK_SPEED = 1380  # Maximum boost clock speed for Nvidia Tesla V100


def plot_histogram(data, xlabel, ylabel, fname, bins=40, dpi=300):
    fig, ax = plt.subplots()
    ax.hist(data, bins=bins)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    agg_text = "mean = {:.2f}\nmedian = {:.2f}\nstd = {:.2f}".format(np.mean(data), np.median(data), np.std(data))
    ax.text(0.75, 0.85, agg_text, transform=ax.transAxes, bbox=dict(fc='white', ec='black', alpha=0.5))
    fig.savefig(fname, dpi=dpi)
    plt.close(fig)


def preprocessing(img):
    content_image = content_transform(img)
    content_image = content_image.cuda()
    content_image = content_image.unsqueeze(0)
    return Variable(content_image)


def inference(ppsd):
    return style_model(ppsd)


style_model = TransformerNet()

models_dir = "models"
path = os.path.join(os.getcwd(), "..", models_dir)
content_transform = transforms.Compose([transforms.ToTensor()])

trial = 300
STARTUP_ONES_SIZE = (trial, 320, 240, 3)  # 360x240, 640x480, 1280x720
sleep_intervals = [0, 2, 5, 10, 15, 20, 30, 50]
torch.set_grad_enabled(False)
np.random.seed(0)
ones = np.random.randint(0, 256, STARTUP_ONES_SIZE, np.uint8)
preprocessed = [preprocessing(ones[idx, :, :, :]) for idx in range(trial)]

for name in os.listdir(path):
    if name.endswith(".model"):
        model = os.path.join(path, name)
        style_model.load_state_dict(torch.load(model))
        style_model.cuda()
        print(name)
        break

gpu_time_record_list = []
sleep_time_record_list = []
for si, sleep_time in enumerate(sleep_intervals):
    # Warm-up
    _ = inference(preprocessed[0])
    torch.cuda.synchronize()

    print(sleep_time)
    sleep_time_secs = sleep_time / 1000
    gpu_time_record = []
    time_slept = []
    total_time = []
    total_timer_start = time.time()
    for i in range(trial):
        # sleep_time = 22.5 + 10. * np.random.randn()  # Randomizing the sleep time will not change the inference time
        if sleep_time > 0:
            sleep_timer_start = time.time()
            sleep_time_elapsed = (time.time() - sleep_timer_start) * 1000      # SPIN LOOP TIMING #####
            while sleep_time_elapsed < sleep_time:                             # SPIN LOOP TIMING #####
                sleep_time_elapsed = (time.time() - sleep_timer_start) * 1000  # SPIN LOOP TIMING #####
            time_slept.append(sleep_time_elapsed)                              # SPIN LOOP TIMING #####
            # time.sleep(sleep_time_secs)                                        # SLEEP TIMING #####
            # sleep_timer_stop = time.time()                                     # SLEEP TIMING #####
            # time_slept.append((sleep_timer_stop - sleep_timer_start) * 1000)   # SLEEP TIMING #####
        starter, ender = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        torch.cuda.synchronize()
        starter.record()
        # t1 = time.time()                               # CPU TIMING #####
        post_inference = inference(preprocessed[i])
        ender.record()
        torch.cuda.synchronize()
        # t2 = time.time()                               # CPU TIMING #####
        # infer_time = (t2 - t1) * 1000                  # CPU TIMING #####
        # gpu_time_record.append(infer_time)             # CPU TIMING #####
        gpu_time = starter.elapsed_time(ender)  # GPU TIMING #####
        gpu_time_record.append(gpu_time)        # GPU TIMING #####
    total_timer_stop = time.time()
    total_time = (total_timer_stop - total_timer_start) * 1000

    plot_histogram(gpu_time_record, 'Time (ms)', 'Count',
                   os.path.join(BASEDIR, "gpu_log", "log-gpu-hist-{}ms.png".format(sleep_time)))
    if time_slept:
        # plot_histogram(time_slept, 'Time (ms)', 'Count',
        #                os.path.join(BASEDIR, "gpu_log", "sleep-time-{}ms.png".format(sleep_time)))
        pass
    else:
        time_slept = [0.] * trial
    gpu_time_record_list.append(gpu_time_record)
    sleep_time_record_list.append(time_slept)

    sleep_plus_inference = (np.mean(time_slept) + np.mean(gpu_time_record)) * trial
    print("({} + {}) * {} = {}, Total = {}, Diff = {}".format(np.mean(time_slept), np.mean(gpu_time_record), trial,
                                                              sleep_plus_inference, total_time,
                                                              total_time - sleep_plus_inference))

    num_frames = len(gpu_time_record)
    fig, ax = plt.subplots()
    ax.set_xlabel('Frame Id')
    ax.set_xlim(0, num_frames)
    ax.set_ylabel('Inference Time (ms)')
    fig.set_figwidth(60)
    num_chosen = num_frames
    p = ax.bar(np.arange(num_chosen), gpu_time_record[:num_chosen], width=1.)
    for i in range(num_chosen):
        ax.text(i, gpu_time_record[:num_chosen][i], int(gpu_time_record[:num_chosen][i]), ha='center', fontsize=10)
    fig.savefig(os.path.join(BASEDIR, "gpu_log", "log-gpu-{}ms.png".format(sleep_time)), dpi=300, bbox_inches="tight")
    plt.close(fig)

fig, ax = plt.subplots()
ax.set_xlabel('Sleep Interval (ms)')
ax.set_ylabel('Inference Time (ms)')
p = ax.errorbar(np.mean(sleep_time_record_list, axis=1), np.mean(gpu_time_record_list, axis=1),
                yerr=[np.mean(gpu_time_record_list, axis=1) - np.percentile(gpu_time_record_list, 2.5, axis=1),
                      np.percentile(gpu_time_record_list, 97.5, axis=1) - np.mean(gpu_time_record_list, axis=1)],
                capsize=3)
fig.savefig(os.path.join(BASEDIR, "gpu_log", "log-gpu-line.png"), dpi=300, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots()
ax.set_xlabel('Time to sleep() (ms)')
ax.set_ylabel('Actual Sleep Time (ms)')
p = ax.errorbar(sleep_intervals, sleep_intervals,
                yerr=[sleep_intervals - np.min(sleep_time_record_list, axis=1),
                      np.max(sleep_time_record_list, axis=1) - sleep_intervals],
                capsize=3)
p = ax.scatter(sleep_intervals, np.mean(sleep_time_record_list, axis=1), marker='x', color='black')
fig.savefig(os.path.join(BASEDIR, "gpu_log", "log-sleep-time-line.png"), dpi=300, bbox_inches="tight")
plt.close(fig)
