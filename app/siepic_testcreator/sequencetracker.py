import os
import importlib.util
import inspect
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DirectoryDict:
    def __init__(self, directory):
        self.directory = directory
        self.dir_dict = self.create_dict_from_dir()
        self.observer = Observer()
        self.handler = self.DirectoryHandler(self)
        self.observer.schedule(self.handler, self.directory, recursive=True)
        self.observer.start()

    def create_dict_from_dir(self):
        """
        Walks through provided directory and creates a dictionary. Each Python file is treated as a Python
        module, and each Python class in the file is included in the dictionary. The file names (without the .py extension)
        are used as dictionary keys and the value for each key is a list of class names.

        Files named '__init__.py' and directories named '__pycache__' and 'core' are explicitly excluded from the walking process.
        Directory walk is performed using os.walk().

        Each module's classes are gathered using the inspect module.

        Returns:
            dict: A dictionary where keys are file names (without .py extension) and values are lists of class
                names present in their respective files.

        Raises:
            ImportError: If the module doesn't exist or can't be imported for some reason.
            Other exceptions may be propagated depending on the content of the Python files.
        """
        dir_dict = {}
        for root, dirs, files in os.walk(self.directory):
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")  # don't visit __pycache__ directories
            if "core" in dirs:
                dirs.remove("core")  # don't visit core directories
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    file_name_without_extension = os.path.splitext(file)[0]
                    module_name = file_name_without_extension
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(
                        module_name, module_path
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    classes = [
                        m[1]
                        for m in inspect.getmembers(
                            module,
                            lambda m: inspect.isclass(m)
                            and m.__module__ == module.__name__,
                        )
                    ]
                    dir_dict[file_name_without_extension] = classes
        return dir_dict

    class DirectoryHandler(FileSystemEventHandler):
        def __init__(self, dir_dict):
            self.dir_dict = dir_dict

        def on_modified(self, event):
            self.dir_dict.dir_dict = self.dir_dict.create_dict_from_dir()
