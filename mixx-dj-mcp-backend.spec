# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['run_server.py'], pathex=['src'],
    datas=[('src/mixx_dj_mcp', 'mixx_dj_mcp')],
    hiddenimports=['uvicorn.logging','uvicorn.loops','uvicorn.loops.asyncio','uvicorn.protocols','uvicorn.protocols.http','uvicorn.protocols.http.httptools_impl','uvicorn.protocols.http.h11_impl','uvicorn.lifespan','uvicorn.lifespan.on'],
    excludes=['tkinter','setuptools','pip','wheel','test','tests','unittest','_distutils_hack'],
    noarchive=True,
)
_keep_dist = ['fastmcp-', 'mcp-', 'prefab_ui-', 'opentelemetry-', 'email_validator-']
_saved = [e for e in a.datas if isinstance(e, tuple) and any(k in str(e[0]) for k in _keep_dist) and '.dist-info' in str(e[0])]
for _list in [a.datas, a.binaries, a.zipfiles, a.scripts]:
    _list[:] = [e for e in _list if not (isinstance(e, tuple) and '.dist-info' in str(e[0]))]
a.datas.extend(_saved)
SKIP = ['torch','playwright','bitsandbytes','llvmlite','pyarrow','pymupdf','grpc','numba','Cython','google','azure','boto3','botocore','matplotlib','PIL','pandas','scipy','sklearn','onnxruntime']
a.binaries = [b for b in a.binaries if not any(s in b[0].lower() for s in SKIP)]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, name='mixx-dj-mcp-backend', debug=False, strip=False, upx=False, upx_exclude=[], runtime_tmpdir=None, console=False)
