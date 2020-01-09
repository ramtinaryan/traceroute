import matplotlib.pyplot as plt

lengthOnLink = [0.03615, 0.06148, 0.08758, 0.10281, 0.13447, ]
lengthCatch_RuleInstallation = [0.02551, 0.0489, 0.07789, 0.09072, 0.12371]
neighborOnLink = [0.10174, 0.19514, 0.30725, 0.34308, 0.44447]
neighborCatch_RuleInstallation = [0.08748, 0.17638, 0.29259, 0.32825, 0.4266]
hedge_approach = [0.06166, 0.11038, 0.16547, 0.20253, 0.25818]
all_approach = [0.03615, 0.06148, 0.08758, 0.10281, 0.13447]
all_approach_worst_sequential = [0.11205, 0.39168, 0.84788, 1.46591, 2.27647]
all_approach_worst_parallel = [0.06625, 0.12568, 0.18998, 0.23711, 0.30457]
per_rule = [25.33, 51.03, 77.1, 103.22, 128.13]
SDNProbe = [1.509068012, 1.815622807,	2.548941135, 3.048414135, 3.45117116]

SDNProbeCatch_RuleInstallation = [0.8240616,
                                  1.539648, 2.1415104, 2.6471448, 3.0740472]

SDNTracerout = [0.39188, 0.93478,	1.47768, 1.72058, 2.16348]

modelGen_Spotlight = [0.0997056, 0.10323, 0.105997, 0.1106078, 0.1109399]
modleGen_SDNProbe = [0.161479, 0.20612, 0.247096, 0.28796, 0.339067]

loop_hedgh_approach_ave = [0.04001, 0.0612, 0.09204, 0.12015, 0.1438]
loop_all_approach_ave = [0.15081,	0.19861, 0.25645, 0.28101, 0.34643]
loop_hedgh_approach_worst = [0.091206, 0.371016, 0.826626, 1.320636, 2.259346]
loop_all_approach_worst_sequential = [
    0.12692, 0.43224, 0.91336, 1.56718, 2.3971]
loop_all_approach_worst_parallel = [0.08112, 0.16624, 0.25546, 0.33838, 0.4252]

x = [5, 10, 15, 20, 25]
totalSW = [10, 20, 30, 40, 50]
pathNo = [471, 880, 1224,	1513, 1757]

# plot with various axes scales

plt.figure(2)
plt.xticks(x, x)
y = lengthOnLink
#plt.plot(x, y)
# plt.yscale('linear')
plt.title('Probing Processing Time')
plt.grid(True)

plt.plot(x, y, '-', lw=2)

plt.ylabel('Processing time (sec)')
plt.xlabel('Hop count')

# plt.show()
plt.figure(1)
y = lengthCatch_RuleInstallation
plt.title('Catch-Rules Installation Processing Time')
plt.grid(True)
plt.xticks(x, x)

plt.plot(x, y, '-', lw=2)
plt.ylabel('Processing time (sec)')
plt.xlabel('Number of neighbrs')

# plt.show()

names = ['SDN Probe', 'SDN Spotlight']
values = [0.0334607, 0.00224]

plt.figure(figsize=(9, 3))

plt.bar(names, values, width=0.3, color=['red', 'blue'])
plt.suptitle('Generating Test Packet')
plt.ylabel('Processing time (sec)')
# plt.show()


names = ['SDN Probe', 'SDN Spotlight']
values = [0.0471451, 0.032042]

plt.figure(figsize=(9, 3))

plt.bar(names, values, width=0.3, color=['red', 'blue'])
plt.suptitle('Generating the network model')
plt.ylabel('Processing time (sec)')
# plt.show()


names = ['SDN Probe', 'SDN Spotlight']
values = [0.910732030869,  0.079913226]

plt.figure(figsize=(9, 3))

plt.bar(names, values, width=0.3, color=['red', 'blue'])
plt.suptitle('Probing process')
plt.ylabel('Processing time (sec)')

# plt.show()

fig, ax1 = plt.subplots()
label = [500, 1000, 1500, 2000, 2500]
plt.xticks(x, label)
plt.title('Hedge-SDNSpotlight and Per-Rule Comparison')

color = 'tab:red'
ax1.set_xlabel('Rule Number')
ax1.set_ylabel('Hedge-SDNSpotlight Processing time (sec)', color=color)
ax1.plot(x, hedge_approach, '-', lw=2, color=color, label="Hagde-SDNSpotlight")
ax1.tick_params(axis='y', labelcolor=color)
ax1.legend(loc="uper left")
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
# we already handled the x-label with ax1
ax2.set_ylabel('Per-Rule Processing time (sec)', color=color)
ax2.plot(x, per_rule, '-^', lw=2, color=color, label="Per-Rule Approach")
ax2.tick_params(axis='y', labelcolor=color)
ax2.legend(loc="lower right")
fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.grid(True)


plt.figure(figsize=(9, 3))

plt.xticks(x, x)

plt.title('Probing Processing Time')
plt.grid(True)

plt.plot(x, hedge_approach, '-', lw=2, label="Hagde Approach")
#plt.plot(x, all_approach, '-', lw=2, label="Open Approach")
plt.plot(x, all_approach_worst_parallel, '-', lw=2,
         label="Open Approach worst case (para)")
plt.plot(x, all_approach_worst_sequential, '-', lw=2,
         label="Open Approach worst case (seq)")
plt.plot(x, SDNProbe, '-', lw=2, label="SDNProbe")
plt.plot(x, SDNTracerout, '-', lw=2, label="SDN Tracerout")
plt.legend(loc="uper left")
plt.ylabel('Processing time (sec)')
plt.xlabel('Path length')


plt.figure(figsize=(9, 3))

plt.xticks(x, x)

plt.title('Hedge and Open Approach Comparison')
plt.grid(True)

plt.plot(x, hedge_approach, '-', lw=2, label="Hagde Approach")
plt.plot(x, all_approach, '-', lw=2, label="Open Approach")
plt.plot(x, all_approach_worst_sequential, '-', lw=2,
         label="Open Approach worst case (seq)")
plt.plot(x, all_approach_worst_parallel, '-', lw=2,
         label="Open Approach worst case (para)")
plt.legend(loc="uper left")
plt.ylabel('Processing time (sec)')
plt.xlabel('Path length')


plt.figure(figsize=(9, 3))

plt.xticks(x, label)

plt.title('Model Generation Processing Time Comparision')
plt.grid(True)

plt.plot(x, modelGen_Spotlight, '-', lw=2, label="SDNSpotlight")
plt.plot(x, modleGen_SDNProbe, '-', lw=2, label="SDNProbe")
plt.legend(loc="uper left")
plt.ylabel('Processing time (sec)')
plt.xlabel('Number of Rules')


plt.figure(figsize=(9, 3))

plt.xticks(x, x)

plt.title('Loop Detection Processing Time (Average)')
plt.grid(True)

plt.plot(x, loop_hedgh_approach_ave, '-', lw=2, label="Hagde Approach")
plt.plot(x, loop_all_approach_ave, '-', lw=2, label="Open Approach")
plt.legend(loc="uper left")
plt.ylabel('Processing time (sec)')
plt.xlabel('Path length')


plt.figure(figsize=(9, 3))

plt.xticks(x, x)

plt.title('Loop Detection Processing Time (Worst Case)')
plt.grid(True)

plt.plot(x, loop_hedgh_approach_worst, '-', lw=2, label="Hagde Approach")
plt.plot(x, loop_all_approach_worst_sequential,
         '-', lw=2, label="Open Approach (seq)")
plt.plot(x, loop_all_approach_worst_parallel,
         '-', lw=2, label="Open Approach (para)")
plt.plot(x, SDNTracerout,'-', lw=2, label="SDN tracerout")
plt.legend(loc="uper left")
plt.ylabel('Processing time (sec)')
plt.xlabel('Path length')


fig = plt.figure()
ax = fig.add_subplot(111, label="1")
ax2 = fig.add_subplot(111, label="2", frame_on=False)
ax.plot(x, lengthCatch_RuleInstallation, '-', lw=2,
        label="SDNSpotlight Approach", color="C0")
ax.set_xlabel("Path Length", color="C0")
ax.set_ylabel("SDNSpotlight processing time (sec)", color="C0")
ax.tick_params(axis='x', colors="C0")
ax.tick_params(axis='y', colors="C0")
ax.legend(loc="uper left")

plt.title('Comparison between Catch-Rules Installation Approaches')
ax2.plot(pathNo, SDNProbeCatch_RuleInstallation, '-^',
         lw=2, label="SDNProbe Approach", color="C1")
ax2.xaxis.tick_top()
ax2.yaxis.tick_right()
ax2.set_xlabel('Path Number', color="C1")
ax2.set_ylabel('SDNProbe processing time (sec)', color="C1")
ax2.xaxis.set_label_position('top')
ax2.yaxis.set_label_position('right')
ax2.tick_params(axis='x', colors="C1")
ax2.tick_params(axis='y', colors="C1")
ax2.legend(loc="lower right")


plt.show()
