import os
import os.path

runners_dir = os.path.join(os.path.dirname(__file__), "runners")

runner_files = [filename for filename in os.listdir(runners_dir) if filename.endswith(".py") and filename != "__init__.py" and os.path.isfile(os.path.join(runners_dir, filename))]

runners = {}

for filename in runner_files:
    module = __import__(filename[:-3])
    Runner = getattr(module, "Runner")
    runners[filename[:-3]] = Runner