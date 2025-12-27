"""
Compatibility shim.

Historically the project imported helpers as `utils.*`.
We moved them to `djangoapp.utils.*` but keep this module to avoid breaking:
- old imports
- migrations referencing `utils.*`
"""