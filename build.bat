echo off

copy /Y "..\p1_gae_global_includes\p1_global_settings.py" includes\
copy /Y "..\p1_gae_global_includes\p1_services.py" includes\
copy /Y "..\p1_gae_global_includes\p1_datastores.py" includes\

copy /Y "..\DGC_donated_code\python_base_includes\GCP_datavalidation\datavalidation.py" includes\
copy /Y "..\DGC_donated_code\python_base_includes\GCP_return_codes\GCP_return_codes.py" includes\
copy /Y "..\DGC_donated_code\python_base_includes\task_queue_functions\task_queue_functions.py" includes\
copy /Y "..\DGC_donated_code\python_base_includes\datastore_functions\datastore_functions.py" includes\
copy /Y "..\DGC_donated_code\python_base_includes\firebase_updater\firebase_updater.py" includes\
copy /Y "..\DGC_donated_code\python_base_includes\error_handling\error_handling.py" includes\



timeout 3