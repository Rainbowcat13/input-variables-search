import matplotlib.pyplot as plt

formulae_sizes, inputs_sizes = [], []
with open('stats/inputs.stat', 'r') as f:
    for line in f:
        f_sz, inp_sz = [int(x) for x in line.strip().split(':')]
        formulae_sizes.append(f_sz)
        inputs_sizes.append(inp_sz)

plt.figure(figsize=(24, 16), dpi=300)
plt.scatter(formulae_sizes, inputs_sizes, s=250, color='red')
plt.xticks(fontsize=40)
plt.yticks(fontsize=40)
plt.xlabel('Количество переменных в формуле', fontsize=50)
plt.ylabel('Количество переменных во входе', fontsize=50)

plt.xscale('log')

plt.title('Взаимосвязь между размером формулы и размером входа', fontsize=50)
plt.grid(True)
plt.savefig('stats/inputs_graphics.png')
