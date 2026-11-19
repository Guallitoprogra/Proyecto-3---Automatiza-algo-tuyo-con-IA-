"""Inicia o cierra únicamente el servidor de esta aplicación."""
import json
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path
BASE=Path(__file__).resolve().parent
URL='http://127.0.0.1:8769' if '--reales' in sys.argv else 'http://127.0.0.1:8768'

def estado(url=URL):
    try:
        with urllib.request.urlopen(url+'/api/datos',timeout=1) as r:
            obj=json.load(r)
            return obj if obj.get('app')=='mi-bolsillo-universitario' else None
    except (OSError,ValueError):return None

def main():
    info=estado()
    if '--cerrar' in sys.argv:
        if info:
            req=urllib.request.Request(URL+'/api/cerrar',data=b'{}',headers={'Content-Type':'application/json','X-App-Token':info['token']},method='POST')
            urllib.request.urlopen(req,timeout=5).close()
        return
    for real,puerto in [(('--reales' in sys.argv), (8769 if '--reales' in sys.argv else 8768))]:
        url=f'http://127.0.0.1:{puerto}'
        if estado(url):continue
        carpeta=BASE/'evidencias'; carpeta.mkdir(exist_ok=True)
        with (carpeta/('servidor_real.log' if real else 'servidor.log')).open('a',encoding='utf-8') as log:
            subprocess.Popen([sys.executable,str(BASE/'servidor.py'),'--port',str(puerto)]+(['--reales'] if real else []),cwd=BASE,stdout=log,stderr=log,
                             creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        for _ in range(40):
            if estado(url):break
            time.sleep(.15)
        else:
            import tkinter.messagebox
            tkinter.messagebox.showerror('Mi bolsillo','No se pudo iniciar el servidor. Revisa evidencias/servidor.log.');return
    webbrowser.open(URL+('/#casos' if '--reales' in sys.argv else ''))

if __name__=='__main__':main()
