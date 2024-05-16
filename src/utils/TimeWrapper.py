import datetime
import time
def convert(n):
    return str(datetime.timedelta(seconds=n))

def wrapper_calc_time(print_log=True):
    """ 
    :param print run time: 
    :return:
    """
    def wrapper(func):
        def inner_wrapper(*args, **kwargs):
            start_time = time.time()
            func_re = func(*args, **kwargs)
            run_time = time.time() - start_time
            # re_time = f'{func.__name__}耗时：{int(tem_time * 1000)}ms'
            converted_time = convert(run_time)
            if print_log:
                print(f"{func.__name__} time:", run_time, converted_time)
            return func_re
        return inner_wrapper
    return wrapper