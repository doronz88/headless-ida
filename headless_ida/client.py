import rpyc
import socket
import os
import subprocess
import builtins


class HeadlessIda():
    IDA_MODULES = ["ida_allins", "ida_auto",
                   "ida_bitrange", "ida_bytes",
                   "ida_dbg", "ida_dirtree", "ida_diskio",
                   "ida_entry", "ida_enum", "ida_expr",
                   "ida_fixup", "ida_fpro", "ida_frame", "ida_funcs",
                   "ida_gdl", "ida_graph",
                   "ida_hexrays",
                   "ida_ida", "ida_idaapi", "ida_idc", "ida_idd", "ida_idp", "ida_ieee",
                   "ida_kernwin",
                   "ida_lines", "ida_loader",
                   "ida_merge", "ida_mergemod", "ida_moves",
                   "ida_nalt", "ida_name", "ida_netnode",
                   "ida_offset",
                   "ida_pro", "ida_problems",
                   "ida_range", "ida_registry",
                   "ida_search", "ida_segment", "ida_segregs", "ida_srclang", "ida_strlist", "ida_struct",
                   "ida_tryblks", "ida_typeinf",
                   "ida_ua",
                   "ida_xref",
                   "idc", "idautils"
                   ]

    def __init__(self, idat_path, binary_path, override_import=True):
        server_path = os.path.join(os.path.realpath(
            os.path.dirname(__file__)), "server.py")
        port = 8000
        with socket.socket() as s:
            s.bind(('', 0))
            port = s.getsockname()[1]
        p = subprocess.Popen(
            f'{idat_path} -A -S"{server_path} {port}" -P+ {binary_path}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            if p.poll() is not None:
                raise Exception(f"IDA failed to start: return code {p.poll()}\n{p.stderr.read().decode()}")
            try:
                self.conn = rpyc.connect("localhost", port)
            except:
                continue
            break

        if override_import:
            self.override_import()

    def override_import(self):
        original_import = builtins.__import__
        def ida_import(name, *args, **kwargs):
            if name in self.IDA_MODULES:
                return self.import_module(name)
            return original_import(name, *args, **kwargs)
        builtins.__import__ = ida_import

    def import_module(self, mod):
        return self.conn.root.import_module(mod)

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()
