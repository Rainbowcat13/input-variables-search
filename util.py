def fullscan_values(assumption, set_size):
    assumption = list(assumption)
    for n in range(2 ** set_size):
        yield [-assumption[j] if (n & (2 ** j)) > 0 else assumption[j] for j in range(set_size)]
