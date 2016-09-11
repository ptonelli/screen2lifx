# -*- coding: utf-8 -*-
# released under LGPL v2

from colorsys import rgb_to_hsv
import logging
import scipy
import scipy.misc
import scipy.cluster
import time

import lifx
from lifx.color import HSBK
import pyscreenshot

NUM_CLUSTERS = 5
DELTA_T = 1000 #ms
LIGHT_NAME = "Salon"

def get_light(light_name):
    lc = lifx.Client()
    time.sleep(1)
    for light in lc:
        if light.label == light_name:
            return light
    raise KeyError("light %s not found" % light_name)

def get_display_main_color():
    img = pyscreenshot.grab()
    img = img.resize((105,65))
    ar = scipy.misc.fromimage(img)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2])
    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
    logging.debug('cluster centres: %s ' % codes)
    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences
    index_max = scipy.argmax(counts)
    return codes[index_max]/255.

def main():
    light = get_light(LIGHT_NAME)
    while True:
        begin = time.time()
        #import ipdb; ipdb.set_trace()
        hsv = list(rgb_to_hsv(*get_display_main_color()) + (3500,))
        hsv[0] = hsv[0] * 360
        new_color = HSBK(*hsv)
        logging.debug("setting to color %s" % str(hsv))
        light.fade_color(new_color, DELTA_T)
        if DELTA_T/1000. - time.time() + begin < 0.:
            logging.warning("refresh setting too short")
        time.sleep(max(DELTA_T/1000. - time.time() + begin, 0))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
