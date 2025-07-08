KeyError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/laporan-keuangan-bumdes-template/app.py", line 89, in <module>
    pd_pendapatan = df_gl[df_gl["Posisi"] == "Pendapatan"]["Kredit"].sum()
                          ~~~~~^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/pandas/core/frame.py", line 4107, in __getitem__
    indexer = self.columns.get_loc(key)
File "/home/adminuser/venv/lib/python3.13/site-packages/pandas/core/indexes/base.py", line 3819, in get_loc
    raise KeyError(key) from err
