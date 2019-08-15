import importlib
import inspect
import sys

from discord.ext import tasks, commands as cmd


# Currently, the module system is just a wrapper over the
# cog and extension system provided by the commands library, with some minor extensions.
# In the future, it might be better to implement this from the ground up,
# including only the features we need.


# We re-export various discord extensions so we could intercept them in the future.
command = cmd.command
group = cmd.group
loop = tasks.loop


parent_module = __name__.rsplit('.', maxsplit=1)[0]


class Module(cmd.Cog):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if hasattr(cls, 'on_unload'):
            cls.cog_unload = cls.on_unload


def get_module_class(name):
    # First we (re)load the python module containing the module class
    module_path = f'{parent_module}.modules.{name}'
    
    if module_path in sys.modules:
        py_module = importlib.reload(sys.modules[module_path])

    else:
        py_module = importlib.import_module(module_path)

    # Get a list of Module subclasses defined in the python module
    module_classes = inspect.getmembers(py_module, lambda x: inspect.isclass(x) and issubclass(x, Module))

    assert len(module_classes) == 1, f'Module {name!r} should define exactly one Module class, not {len(module_classes)}'

    module_class = module_classes[0][1]

    # Make sure the cog and the module system use the same name.
    # This will become unneccessary if we ever stop using the cog system.
    module_class.__cog_name__ = name

    # inspect.getmembers returns (name, member) tuples.
    # We only want the member, not the name.
    return module_classes[0][1]