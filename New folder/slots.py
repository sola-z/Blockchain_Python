from time import time
import math


begin_epoch_time = 1462953000
interval = 10
delegates = 20


def get_epoch_time(time_now=None):
    if time_now is None:
        time_now = time()
    return math.floor(time_now - begin_epoch_time)


def get_time(time_now):
    return get_epoch_time(time_now)


def get_real_time(epoch_time=None):
    if epoch_time is None:
        epoch_time = get_time(time())
    return (begin_epoch_time + epoch_time) * 1000


# return which slots this epochTime belongs to
def get_slot_number(epoch_time=None):
    if epoch_time is None:
        epoch_time = get_time(time())
    return math.floor(epoch_time / interval)


# return current slots's corresponding time (epoch)
def get_slot_time(slot):
    return slot * interval


def get_next_slot():
    slot = get_slot_number()
    return slot+1


def get_last_slot(next_slot):
    return next_slot + delegates
