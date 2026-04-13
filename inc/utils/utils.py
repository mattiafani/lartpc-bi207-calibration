import inc
from inc.settings import debug


def parse_args(args, default_args):
    if len(args) == 6:
        print(f'\n{inc.settings.output_align}- Arguments OK. Running with INPUT parameters')
        return args[1], bool(int(args[2])), bool(int(args[3])), bool(int(args[4])), bool(int(args[5])), True
    print(f'\n{inc.settings.output_align}! Arguments not found. Running with DEFAULT parameters')
    return (default_args['raw_data_folder_name'], default_args['input_evtdisplay_bool'],
            default_args['input_chndisplay_bool'], default_args['input_equalize_bool'],
            default_args['input_filter_bool'], False)


def most_frequent(list_):
    return max(set(list_), key=list_.count)


def debug_print(msg):
    if debug:
        print(msg)


def two_argmax(strip_plane_maxima):
    return [j[0] for j in sorted(strip_plane_maxima, key=lambda v: v[1])[-2:]]


def local_maxima(strip_plane, offset):
    loc_maxima = [(i + offset, val) for i, val in enumerate(strip_plane)
                  if 0 < i < len(strip_plane) - 1 and val > strip_plane[i-1] and val > strip_plane[i+1]]
    if len(loc_maxima) < 2:
        return [(i + offset, val) for i, val in enumerate(strip_plane)
                if 0 < i < len(strip_plane) - 1 and val >= strip_plane[i - 1] and val >= strip_plane[i + 1]]
    return loc_maxima
