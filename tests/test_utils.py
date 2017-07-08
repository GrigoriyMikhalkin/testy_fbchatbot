import os


def set_env_variable(env_var, value):
    """
    Set environmental variable value for test
    then return to original value

    :param: env_var: str: environmental variable
    :param: value: str
    """
    def func_wrapper(f):
        def args_wrapper(*args, **kwargs):
            old_value = os.environ.get(env_var, '')
            os.environ[env_var] = value

            res = f(*args, **kwargs)
            os.environ[env_var] = old_value
            return res
        return args_wrapper
    return func_wrapper
