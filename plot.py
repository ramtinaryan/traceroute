import matplotlib.pyplot as plt

lengthOnLink = [0.03615, 0.06148, 0.08758, 0.10281, 0.13447, ]
lengthCatch_RuleInstallation = [0.02551, 0.0489, 0.07789, 0.09072, 0.12371]
neighborOnLink = [0.10174, 0.19514, 0.30725, 0.34308, 0.44447]
neighborCatch_RuleInstallation = [0.08748, 0.17638, 0.29259, 0.32825, 0.4266]


x = [5, 10, 15, 20, 25]

# plot with various axes scales

plt.figure(2)

y = lengthOnLink
#plt.plot(x, y)
# plt.yscale('linear')
plt.title('Probing Processing Time')
plt.grid(True)

plt.plot(x, y, '-', lw=2)

plt.ylabel('Processing time (sec)')
plt.xlabel('Hop count)')

# plt.show()
plt.figure(1)
y = lengthCatch_RuleInstallation
plt.title('Catch-Rules Installation Processing Time')
plt.grid(True)

plt.plot(x, y, '-', lw=2)
plt.ylabel('Processing time (sec)')
plt.xlabel('Number of neighbrs')
https: // www.sharelatex.com / project

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

plt.show()
