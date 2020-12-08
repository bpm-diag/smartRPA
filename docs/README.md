# Sphinx documentation instructions

## Build
In order to build Sphinx documentation, cd into `/docs` folder and run
```bash
make github
```

## Edit
To edit documentation, cd into `/docs/source/modules`.
Here you can find all the rst of the modules.

If you want to document a new class/method, add the following block in a .rst file:
```
.. automodule:: path.to.module (e.g. modules.GUI.segmentationDialog)
   :members:
   :private-members:
```