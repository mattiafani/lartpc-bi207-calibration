# /usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt


def plot_histogram(data, filename, title, xlabel, ylabel, color, isbatchbool):
    plt.hist(data, bins=max(data), color=color, alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.5)
    plt.xlabel(xlabel, fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.title(title, fontsize=18)
    plt.xticks(range(1, 49, 5), fontsize=14)
    plt.yticks(fontsize=14)
    plt.savefig(filename, format='pdf')
    if not isbatchbool:
        plt.show()

    plt.close()


def plot_scatter_histo(data, filename, title, xlabel, ylabel, color, isbatchbool):
    x = range(49)
    y = data[:49]

    plt.bar(x, y)
    plt.title(title, fontsize=18)
    plt.xlabel(xlabel, fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.xticks(range(1, 49, 5), fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis='y', alpha=0.5)

    plt.savefig(filename, format='pdf')

    if not isbatchbool:
        plt.show()

    plt.close()
